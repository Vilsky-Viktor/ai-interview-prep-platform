import asyncio
import json
import uuid

from app.constants.events import CONSUMER_GROUP, EVENTS_STREAM
from app.services import answer_events
from app.storage import quality

QUESTION_ID = uuid.uuid4()


class FakeRedis:
    def __init__(self):
        self.acked = []

    async def xack(self, stream, group, entry_id):
        self.acked.append((stream, group, entry_id))


def recorded():
    data = {
        "question_id": str(QUESTION_ID),
        "question_text": "Which account is debited?",
        "option": "Cash",
        "correct": True,
    }

    return {"type": "answer.recorded", "data": json.dumps(data)}


def test_recorded_answer_goes_into_the_question_statistics(monkeypatch):
    stored = []

    async def record_answer(question_id, question_text, option, correct):
        stored.append((question_id, question_text, option, correct))

    monkeypatch.setattr(quality, "record_answer", record_answer)
    redis = FakeRedis()

    asyncio.run(answer_events.process(redis, "1-0", recorded()))

    assert stored == [(QUESTION_ID, "Which account is debited?", "Cash", True)]
    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "1-0")]


def test_other_events_are_acknowledged_without_action():
    redis = FakeRedis()

    asyncio.run(answer_events.process(redis, "2-0", {"type": "preparation.shared", "data": "{}"}))

    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "2-0")]


def test_failed_store_stays_pending_for_a_retry(monkeypatch):
    async def database_down(*args):
        raise ConnectionError("database is down")

    monkeypatch.setattr(quality, "record_answer", database_down)
    redis = FakeRedis()

    asyncio.run(answer_events.process(redis, "3-0", recorded()))

    assert redis.acked == []
