import asyncio

import pytest
from fastapi import HTTPException

from app.constants.notifications import MAX_STREAMS_PER_USER
from app.services import feed


class FakeRedis:
    def __init__(self):
        self.counts = {}

    async def incr(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1

        return self.counts[key]

    async def decr(self, key):
        self.counts[key] -= 1

    async def expire(self, key, seconds):
        pass


@pytest.fixture
def redis(monkeypatch):
    fake = FakeRedis()

    async def changes(user_id):
        yield ": connected\n\n"

    monkeypatch.setattr(feed, "get_redis", lambda: fake)
    monkeypatch.setattr(feed, "changes", changes)

    return fake


async def read(stream):
    return [chunk async for chunk in stream]


def test_a_user_holds_a_limited_number_of_streams_and_a_closed_one_frees_its_slot(redis):
    async def scenario():
        streams = [await feed.open_stream("ann") for _ in range(MAX_STREAMS_PER_USER)]

        with pytest.raises(HTTPException) as refused:
            await feed.open_stream("ann")

        assert refused.value.status_code == 429
        # Another user isn't held back by Ann's tabs.
        await read(await feed.open_stream("bob"))
        # One of Ann's streams ends: its slot is free again.
        await read(streams[0])

        return await feed.open_stream("ann")

    asyncio.run(scenario())

    assert redis.counts["streams:user:ann"] == MAX_STREAMS_PER_USER
