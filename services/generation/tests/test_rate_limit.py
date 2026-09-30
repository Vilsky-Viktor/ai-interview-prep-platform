import asyncio

import pytest
from fastapi import HTTPException

from app.helpers.rate_limit import hit


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def set(self, key: str, value: int, ex: int, nx: bool):
        self.commands.append(("set", key, value, ex, nx))

    def incr(self, key: str):
        self.commands.append(("incr", key))

    async def execute(self) -> list:
        results = []

        for command in self.commands:
            if command[0] == "set":
                _, key, value, ex, nx = command
                created = not (nx and key in self.redis.counts)

                if created:
                    self.redis.counts[key] = value
                    self.redis.ttls[key] = ex

                results.append(created)
            else:
                self.redis.counts[command[1]] += 1
                results.append(self.redis.counts[command[1]])

        return results


class FakeRedis:
    def __init__(self):
        self.counts: dict[str, int] = {}
        self.ttls: dict[str, int] = {}

    def pipeline(self, transaction: bool):
        return FakePipeline(self)


def test_hit_allows_up_to_the_limit():
    redis = FakeRedis()
    asyncio.run(hit(redis, "rate:generations:u1", 2, 60))
    asyncio.run(hit(redis, "rate:generations:u1", 2, 60))

    assert redis.counts["rate:generations:u1"] == 2
    assert redis.ttls["rate:generations:u1"] == 60


def test_hit_rejects_over_the_limit():
    redis = FakeRedis()
    asyncio.run(hit(redis, "rate:generations:u1", 1, 60))

    with pytest.raises(HTTPException) as error:
        asyncio.run(hit(redis, "rate:generations:u1", 1, 60))

    assert error.value.status_code == 429


def test_hit_skips_when_limit_is_zero():
    redis = FakeRedis()
    asyncio.run(hit(redis, "rate:generations:u1", 0, 60))

    assert redis.counts == {}


def test_hit_keeps_the_first_expiry():
    redis = FakeRedis()
    asyncio.run(hit(redis, "rate:generations:u1", 5, 60))
    redis.ttls["rate:generations:u1"] = 30
    asyncio.run(hit(redis, "rate:generations:u1", 5, 60))

    assert redis.counts["rate:generations:u1"] == 2
    assert redis.ttls["rate:generations:u1"] == 30
