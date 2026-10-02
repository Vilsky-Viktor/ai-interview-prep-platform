import asyncio
import uuid

from app.integrations import library, openai_batch
from app.models.key_checks import KeyCheck as KeyCheckRow
from app.services import key_check_batches
from app.storage import key_checks
from tests.test_verify import TEXT, context, question

KEPT = uuid.uuid4()
GONE = uuid.uuid4()


class FakeStore:
    """key_checks storage in memory: question id -> batch id (None while waiting)."""

    def __init__(self, rows):
        self.rows = dict(rows)

    def install(self, monkeypatch):
        async def unsent():
            return [row(qid) for qid, batch in self.rows.items() if batch is None]

        async def sent_batches():
            return sorted({batch for batch in self.rows.values() if batch})

        async def in_batch(batch_id):
            return [row(qid) for qid, batch in self.rows.items() if batch == batch_id]

        async def set_batch(question_ids, batch_id):
            self.rows.update({qid: batch_id for qid in question_ids})

        async def remove(question_ids):
            for qid in question_ids:
                self.rows.pop(qid, None)

        for name, fake in [
            ("unsent", unsent),
            ("sent_batches", sent_batches),
            ("in_batch", in_batch),
            ("set_batch", set_batch),
            ("remove", remove),
        ]:
            monkeypatch.setattr(key_checks, name, fake)


def row(question_id):
    return KeyCheckRow(question_id=question_id, question_text=TEXT)


def library_with(monkeypatch, existing):
    async def fake_context(question_id):
        return context() if question_id in existing else None

    async def fake_quality(question_id):
        return question() if question_id in existing else None

    monkeypatch.setattr(library, "get_question_context", fake_context)
    monkeypatch.setattr(library, "get_question_quality", fake_quality)


def test_waiting_checks_go_out_in_one_batch(monkeypatch):
    store = FakeStore({KEPT: None, GONE: None})
    store.install(monkeypatch)
    library_with(monkeypatch, {KEPT})
    sent = {}

    async def fake_submit(requests):
        sent.update(requests)

        return "batch-1"

    monkeypatch.setattr(openai_batch, "submit", fake_submit)

    asyncio.run(key_check_batches.submit_pending())

    assert list(sent) == [str(KEPT)]
    assert sent[str(KEPT)]["reasoning_effort"] == "medium"
    assert TEXT in sent[str(KEPT)]["messages"][0]["content"]
    # A question deleted since it was flagged is dropped.
    assert store.rows == {KEPT: "batch-1"}


def test_a_finished_batch_is_applied_and_bad_replies_are_checked_right_away(monkeypatch):
    other = uuid.uuid4()
    store = FakeStore({KEPT: "batch-1", other: "batch-1"})
    store.install(monkeypatch)
    library_with(monkeypatch, {KEPT, other})
    applied = []

    async def fake_status(batch_id):
        return "completed", "file-1"

    async def fake_results(file_id):
        return {str(KEPT): '{"correct_index": 0}', str(other): None}

    async def fake_apply(question_id, question, context, result):
        applied.append((question_id, result.correct_index))

    async def fake_check_now(question_id, question, context):
        applied.append((question_id, "checked now"))

    monkeypatch.setattr(openai_batch, "status", fake_status)
    monkeypatch.setattr(openai_batch, "results", fake_results)
    monkeypatch.setattr(key_check_batches, "apply_key_check", fake_apply)
    monkeypatch.setattr(key_check_batches, "check_key", fake_check_now)

    asyncio.run(key_check_batches.collect_finished())

    assert sorted(applied, key=str) == sorted([(KEPT, 0), (other, "checked now")], key=str)
    assert store.rows == {}


def test_an_expired_batch_is_sent_again(monkeypatch):
    store = FakeStore({KEPT: "batch-1"})
    store.install(monkeypatch)

    async def fake_status(batch_id):
        return "expired", None

    monkeypatch.setattr(openai_batch, "status", fake_status)

    asyncio.run(key_check_batches.collect_finished())

    assert store.rows == {KEPT: None}


def test_a_running_batch_is_left_alone(monkeypatch):
    store = FakeStore({KEPT: "batch-1"})
    store.install(monkeypatch)

    async def fake_status(batch_id):
        return "in_progress", None

    monkeypatch.setattr(openai_batch, "status", fake_status)

    asyncio.run(key_check_batches.collect_finished())

    assert store.rows == {KEPT: "batch-1"}
