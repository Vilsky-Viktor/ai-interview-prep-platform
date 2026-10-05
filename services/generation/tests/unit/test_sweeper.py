import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.dialects import postgresql

from app.constants.generation import GENERATION_STOPPED, STUCK_AFTER_SECONDS
from app.models.generation import Generation
from app.services import jobs, schedules
from app.storage import generations


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

        return []

    monkeypatch.setattr(generations, "fail_stuck", fake_fail_stuck)
    no_finished_threads(monkeypatch)

    asyncio.run(schedules.sweep(FakeCheckpointer()))

    [(before, error)] = calls
    expected = datetime.now(UTC) - timedelta(seconds=STUCK_AFTER_SECONDS)
    assert abs((before - expected).total_seconds()) < 5
    assert error == GENERATION_STOPPED


def test_sweep_deletes_checkpoints_of_finished_generations(monkeypatch):
    async def fake_fail_stuck(before, error):
        return []

    checkpointer = FakeCheckpointer()
    monkeypatch.setattr(generations, "fail_stuck", fake_fail_stuck)
    no_finished_threads(monkeypatch, ["done-1", "cancelled-1"])

    asyncio.run(schedules.sweep(checkpointer))

    assert checkpointer.deleted == ["done-1", "cancelled-1"]


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
    fake_session(monkeypatch, statements)

    asyncio.run(generations.fail_stuck(datetime.now(UTC), GENERATION_STOPPED))

    sql = compiled(statements[0])
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


def test_the_worker_runs_schedules_and_jobs_through_its_routes(monkeypatch):
    from fastapi.testclient import TestClient

    from app.worker_main import app as worker_app

    called = []

    async def record(*args):
        called.append(args)

    for name in ("sweep", "key_check_batches", "retention"):
        monkeypatch.setattr(schedules, name, lambda *args, name=name: record(name))

    monkeypatch.setattr(jobs, "run_pipeline", record)
    worker_app.state.checkpointer = "checkpointer"
    worker_app.state.graph = "graph"
    client = TestClient(worker_app)

    for path in ("sweep", "key-check-batches", "retention"):
        assert client.post(f"/internal/schedules/{path}").status_code == 204

    assert called == [("sweep",), ("key_check_batches",), ("retention",)]


def test_worker_skips_a_generation_the_sweeper_already_failed(monkeypatch):
    started = []

    async def get(_generation_id):
        return Generation(id=uuid.uuid4(), status="failed", kind="interview")

    async def run_pipeline(*args):
        started.append(args)

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(jobs, "run_pipeline", run_pipeline)

    asyncio.run(jobs.run_generation(None, uuid.uuid4(), None))

    assert started == []
