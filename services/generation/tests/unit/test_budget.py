import asyncio
import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.config.settings import settings
from app.constants.generation import GENERATIONS_PAUSED
from app.routers import internal
from app.service_auth import service_token
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


def test_a_company_that_paid_isnt_held_to_the_limit_free_accounts_used_up(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(budget, "get_redis", lambda: redis)
    monkeypatch.setattr(settings, "daily_generation_limit", 1)
    asyncio.run(budget.use_daily_budget())

    with pytest.raises(HTTPException):
        asyncio.run(budget.use_daily_budget(paid=False))

    asyncio.run(budget.use_daily_budget(paid=True))

    # A paying company's generations don't count either, so they never use it up.
    assert list(redis.counts.values()) == [2]


@pytest.mark.parametrize("paid", [False, True])
def test_a_regenerated_question_counts_toward_the_limit_unless_the_company_paid(
    client, monkeypatch, paid
):
    set_id = uuid.uuid4()
    counted = []

    async def context(question_id):
        return SimpleNamespace(set_id=set_id)

    async def allowed(*args):
        pass

    async def daily(paid=False):
        counted.append(paid)

    async def regenerated(question_id, found):
        return {"id": str(question_id), "text": "New question?", "options": []}

    monkeypatch.setattr(internal.library, "get_question_context", context)
    monkeypatch.setattr(internal, "hit", allowed)
    monkeypatch.setattr(internal, "use_daily_budget", daily)
    monkeypatch.setattr(internal, "regenerate", regenerated)

    client.post(
        f"/internal/questions/{uuid.uuid4()}/regenerate",
        json={"user_id": "bob", "set_id": str(set_id), "paid": paid},
        headers={"Authorization": f"Bearer {service_token('generation')}"},
    )

    assert counted == [paid]
