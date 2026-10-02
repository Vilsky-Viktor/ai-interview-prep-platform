import asyncio

import pytest
from fastapi import HTTPException

from app.config.settings import settings
from app.constants.generation import GENERATIONS_PAUSED
from app.services import budget


class FakePipeline:
    def __init__(self, counts):
        self.counts = counts
        self.key = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def incr(self, key):
        self.key = key

    def expire(self, key, seconds):
        pass

    async def execute(self):
        self.counts[self.key] = self.counts.get(self.key, 0) + 1

        return [self.counts[self.key], True]


class FakeRedis:
    def __init__(self):
        self.counts = {}

    def pipeline(self, transaction):
        return FakePipeline(self.counts)


def test_generations_past_the_daily_limit_wait_until_tomorrow(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(budget, "get_redis", lambda: redis)
    monkeypatch.setattr(settings, "daily_generation_limit", 2)

    asyncio.run(budget.use_daily_budget())
    asyncio.run(budget.use_daily_budget())

    with pytest.raises(HTTPException) as paused:
        asyncio.run(budget.use_daily_budget())

    assert paused.value.status_code == 503
    assert paused.value.detail == GENERATIONS_PAUSED
    [key] = redis.counts
    assert key.startswith("budget:generations:")


def test_no_limit_counts_nothing(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(budget, "get_redis", lambda: redis)
    monkeypatch.setattr(settings, "daily_generation_limit", 0)

    asyncio.run(budget.use_daily_budget())

    assert redis.counts == {}
