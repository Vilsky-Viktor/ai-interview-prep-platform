import asyncio
import json
import uuid

from app.constants.events import CONSUMER_GROUP, EVENTS_STREAM
from app.services import generation_events
from app.storage import interviews

GENERATION_ID = uuid.uuid4()
SET_ID = uuid.uuid4()


class FakeRedis:
    def __init__(self):
        self.acked = []

    async def xack(self, stream, group, entry_id):
        self.acked.append((stream, group, entry_id))


def completed():
    data = {
        "generation_id": str(GENERATION_ID),
        "company_id": str(uuid.uuid4()),
        "set_id": str(SET_ID),
        "title": "Bookkeeper interview",
    }

    return {"type": "generation.completed", "data": json.dumps(data)}


def test_finished_generation_is_stored_on_its_interview(monkeypatch):
    stored = []

    async def set_generated(generation_id, set_id, title):
        stored.append((generation_id, set_id, title))

    monkeypatch.setattr(interviews, "set_generated", set_generated)
    redis = FakeRedis()

    asyncio.run(generation_events.process(redis, "1-0", completed()))

    assert stored == [(GENERATION_ID, SET_ID, "Bookkeeper interview")]
    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "1-0")]


def test_other_events_are_acknowledged_without_action(monkeypatch):
    redis = FakeRedis()

    asyncio.run(
        generation_events.process(redis, "2-0", {"type": "candidate.invited", "data": "{}"})
    )

    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "2-0")]


def test_failed_store_stays_pending_for_a_retry(monkeypatch):
    async def database_down(*args):
        raise ConnectionError("database is down")

    monkeypatch.setattr(interviews, "set_generated", database_down)
    redis = FakeRedis()

    asyncio.run(generation_events.process(redis, "3-0", completed()))

    assert redis.acked == []


def test_an_expired_review_removes_its_interview(monkeypatch):
    removed = []

    async def remove_for_generation(generation_id):
        removed.append(generation_id)

    monkeypatch.setattr(interviews, "remove_for_generation", remove_for_generation)
    redis = FakeRedis()
    event = {
        "type": "generation.cancelled",
        "data": json.dumps({"generation_id": str(GENERATION_ID)}),
    }

    asyncio.run(generation_events.process(redis, "4-0", event))

    assert removed == [GENERATION_ID]
    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "4-0")]
