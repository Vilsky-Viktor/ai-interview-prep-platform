import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.dialects import postgresql

from app.constants.generation import GENERATION_STOPPED, STUCK_AFTER_SECONDS
from app.models.generation import Generation
from app.storage import generations
from app.workers import generation as worker


class FakeCheckpointer:
    def __init__(self):
        self.deleted = []

    async def adelete_thread(self, thread_id):
        self.deleted.append(thread_id)


def no_finished_threads(monkeypatch, threads=(), expired=()):
    async def fake_threads():
        return list(threads)

    async def fake_expire(before):
        return list(expired)

    monkeypatch.setattr(generations, "finished_threads", fake_threads)
    monkeypatch.setattr(generations, "expire_reviews", fake_expire)


def test_sweep_fails_generations_untouched_for_longer_than_a_job_may_run(monkeypatch):
    calls = []

    async def fake_fail_stuck(before, error):
        calls.append((before, error))

        return 1

    monkeypatch.setattr(generations, "fail_stuck", fake_fail_stuck)
    no_finished_threads(monkeypatch)

    asyncio.run(worker.sweep({"checkpointer": FakeCheckpointer()}))

    [(before, error)] = calls
    expected = datetime.now(UTC) - timedelta(seconds=STUCK_AFTER_SECONDS)
    assert abs((before - expected).total_seconds()) < 5
    assert error == GENERATION_STOPPED


def test_sweep_deletes_checkpoints_of_finished_generations(monkeypatch):
    async def fake_fail_stuck(before, error):
        return 0

    checkpointer = FakeCheckpointer()
    monkeypatch.setattr(generations, "fail_stuck", fake_fail_stuck)
    no_finished_threads(monkeypatch, ["done-1", "cancelled-1"])

    asyncio.run(worker.sweep({"checkpointer": checkpointer}))

    assert checkpointer.deleted == ["done-1", "cancelled-1"]


def test_expired_reviews_remove_their_interviews(monkeypatch):
    async def fake_fail_stuck(before, error):
        return 0

    interview = Generation(id=uuid.uuid4(), kind="interview", status="cancelled")
    preparation = Generation(id=uuid.uuid4(), kind="preparation", status="cancelled")
    published = []

    async def fake_publish(event_type, data):
        published.append((event_type, data))

    monkeypatch.setattr(generations, "fail_stuck", fake_fail_stuck)
    monkeypatch.setattr(worker.events, "publish", fake_publish)
    no_finished_threads(monkeypatch, expired=[interview, preparation])

    asyncio.run(worker.sweep({"checkpointer": FakeCheckpointer()}))

    assert published == [("generation.cancelled", {"generation_id": str(interview.id)})]


def fake_session(monkeypatch, statements, rowcount=0):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def execute(self, statement):
            statements.append(statement)

            class Result:
                pass

            Result.rowcount = rowcount

            return Result()

        async def scalars(self, statement):
            statements.append(statement)

            return []

        async def commit(self):
            pass

    monkeypatch.setattr(generations, "Session", FakeSession)


def compiled(statement) -> str:
    return str(
        statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    )


def test_only_queued_and_running_rows_are_swept(monkeypatch):
    statements = []
    fake_session(monkeypatch, statements, rowcount=2)

    count = asyncio.run(generations.fail_stuck(datetime.now(UTC), GENERATION_STOPPED))

    sql = compiled(statements[0])
    assert count == 2
    assert "status IN ('queued', 'running')" in sql
    assert "updated_at <" in sql
    assert "'failed'" in sql


def test_only_done_and_cancelled_checkpoints_are_deleted(monkeypatch):
    statements = []
    fake_session(monkeypatch, statements)

    asyncio.run(generations.finished_threads())

    sql = compiled(statements[0])
    assert "IN ('done', 'cancelled')" in sql
    assert "failed" not in sql and "awaiting_review" not in sql


def test_sweeper_key_check_batches_and_retention_run_on_a_schedule():
    jobs = [job.coroutine for job in worker.WorkerSettings.cron_jobs]

    assert jobs == [worker.sweep, worker.key_check_batches, worker.retention]


def test_worker_skips_a_generation_the_sweeper_already_failed(monkeypatch):
    started = []

    async def get(_generation_id):
        return Generation(id=uuid.uuid4(), status="failed", kind="preparation")

    async def run_pipeline(*args):
        started.append(args)

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(worker, "run_pipeline", run_pipeline)

    asyncio.run(worker.run_generation({"graph": None}, str(uuid.uuid4())))

    assert started == []
