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

    monkeypatch.setattr(limits, "hit", hit)
    monkeypatch.setattr(limits, "spend", spend)

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

    monkeypatch.setattr(limits, "spend", spend)
    asyncio.run(limits.record(None, "ann", COMPANY, 1_234))

    assert added == [
        ("spend:assistant:user:ann", 1_234),
        (f"spend:assistant:company:{COMPANY}", 1_234),
        ("spend:assistant:all", 1_234),
    ]
