import asyncio

import pytest
from fastapi import HTTPException

from app.constants.limits import (
    MESSAGES_PER_COMPANY_DAY,
    MESSAGES_PER_DAY,
    MESSAGES_PER_USER_DAY,
    MESSAGES_PER_USER_HOUR,
    TOKENS_PER_COMPANY_DAY,
    TOKENS_PER_DAY,
    TOKENS_PER_USER_DAY,
    TRANSCRIPTIONS_PER_USER_HOUR,
)
from app.services import limits

COMPANY = "8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f"


@pytest.fixture
def counted(monkeypatch):
    """The counters and budgets each call reads, in order."""
    made = []

    async def hit(redis, key, limit, window):
        made.append(("hit", key, limit))

    async def spend(redis, key, amount, limit, window):
        made.append(("spend", key, amount, limit))

    async def unpaid(redis, company_id):
        return False

    monkeypatch.setattr(limits, "hit", hit)
    monkeypatch.setattr(limits, "spend", spend)
    monkeypatch.setattr(limits, "company_paid", unpaid)

    return made


def test_a_message_checks_every_budget_then_counts_against_every_limit(counted):
    asyncio.run(limits.check(None, "ann", COMPANY))

    assert counted == [
        ("spend", "spend:assistant:user:ann", 0, TOKENS_PER_USER_DAY),
        ("spend", f"spend:assistant:company:{COMPANY}", 0, TOKENS_PER_COMPANY_DAY),
        ("spend", "spend:assistant:all", 0, TOKENS_PER_DAY),
        ("hit", "rate:assistant:hour:ann", MESSAGES_PER_USER_HOUR),
        ("hit", "rate:assistant:day:ann", MESSAGES_PER_USER_DAY),
        ("hit", f"rate:assistant:company:{COMPANY}", MESSAGES_PER_COMPANY_DAY),
        ("hit", "rate:assistant:all", MESSAGES_PER_DAY),
    ]


def test_a_company_that_paid_isnt_held_to_everyones_limits(counted, monkeypatch):
    async def paid(redis, company_id):
        return True

    monkeypatch.setattr(limits, "company_paid", paid)
    asyncio.run(limits.check(None, "ann", COMPANY))

    assert not any(item[1].endswith(":all") for item in counted)
    assert ("hit", f"rate:assistant:company:{COMPANY}", MESSAGES_PER_COMPANY_DAY) in counted


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex):
        self.values[key] = value


def test_whether_a_company_paid_is_asked_of_billing_once_in_a_while(monkeypatch):
    asked = []

    async def from_billing(company_id):
        asked.append(company_id)

        return True

    monkeypatch.setattr(limits.billing, "company_paid", from_billing)
    redis = FakeRedis()

    assert asyncio.run(limits.company_paid(redis, COMPANY)) is True
    assert asyncio.run(limits.company_paid(redis, COMPANY)) is True
    assert asyncio.run(limits.company_paid(redis, None)) is False
    assert asked == [COMPANY]


def test_without_a_company_only_the_users_and_everyones_count(counted):
    asyncio.run(limits.check(None, "ann", None))

    assert not any("company" in item[1] for item in counted)


def test_a_turns_tokens_are_added_and_going_over_never_fails_the_turn(monkeypatch):
    added = []

    async def spend(redis, key, amount, limit, window):
        added.append((key, amount))

        if "user" in key:
            raise HTTPException(429, "over")

        if "all" in key:
            raise ConnectionError("Redis is down")

    async def unpaid(redis, company_id):
        return False

    monkeypatch.setattr(limits, "spend", spend)
    monkeypatch.setattr(limits, "company_paid", unpaid)
    asyncio.run(limits.record(None, "ann", COMPANY, 1_234))

    assert added == [
        ("spend:assistant:user:ann", 1_234),
        (f"spend:assistant:company:{COMPANY}", 1_234),
        ("spend:assistant:all", 1_234),
    ]


def test_a_voice_message_checks_the_users_and_everyones_budgets_and_its_own_limit(counted):
    asyncio.run(limits.check_transcription(None, "ann"))

    assert counted == [
        ("spend", "spend:assistant:user:ann", 0, TOKENS_PER_USER_DAY),
        ("spend", "spend:assistant:all", 0, TOKENS_PER_DAY),
        ("hit", "rate:assistant:transcribe:hour:ann", TRANSCRIPTIONS_PER_USER_HOUR),
    ]
