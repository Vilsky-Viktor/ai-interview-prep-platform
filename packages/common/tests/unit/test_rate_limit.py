import asyncio

import pytest
from fastapi import HTTPException
from prepza_common.rate_limit import hit, hit_emails, spend

from tests.unit.fake_redis import FakeRedis


def statuses(calls):
    """200 for each call that passed, 429 for each one the limit refused."""
    codes = []

    for call in calls:
        try:
            asyncio.run(call())
            codes.append(200)
        except HTTPException as error:
            codes.append(error.status_code)

    return codes


def test_hit_refuses_past_the_limit():
    redis = FakeRedis()

    assert statuses([lambda: hit(redis, "key", 2, 60)] * 3) == [200, 200, 429]


def test_a_zero_limit_is_off():
    redis = FakeRedis()

    assert statuses([lambda: hit(redis, "key", 0, 60)] * 5) == [200] * 5
    assert redis.counts == {}


def test_emails_are_limited_per_recipient():
    redis = FakeRedis()

    def invite(recipient):
        return lambda: hit_emails(redis, "ann", recipient, 30, 200, 3)

    assert statuses([invite("set-1:bob@example.com")] * 4) == [200, 200, 200, 429]
    # Another address, or the same one for something else, has its own count.
    assert statuses([invite("set-1:carol@example.com"), invite("set-2:bob@example.com")]) == [
        200,
        200,
    ]


def test_emails_are_limited_per_sender_across_recipients():
    redis = FakeRedis()
    calls = [
        lambda i=i: hit_emails(redis, "ann", f"set-1:{i}@example.com", 2, 200, 3) for i in range(3)
    ]

    assert statuses(calls) == [200, 200, 429]


@pytest.mark.parametrize("limit", [-1, 0])
def test_non_positive_limits_never_refuse(limit):
    redis = FakeRedis()

    assert statuses([lambda: hit(redis, "key", limit, 60)] * 3) == [200, 200, 200]


def test_spend_refuses_once_the_total_is_over_the_limit():
    redis = FakeRedis()
    calls = [lambda amount=amount: spend(redis, "key", amount, 100, 60) for amount in (60, 40, 1)]

    assert statuses(calls) == [200, 200, 429]
    assert redis.counts == {"key": 101}


def test_spending_nothing_only_checks_the_budget():
    redis = FakeRedis()

    def check():
        return spend(redis, "key", 0, 20, 60)

    assert statuses([check, lambda: spend(redis, "key", 25, 20, 60), check]) == [200, 429, 429]
    assert redis.counts == {"key": 25}


@pytest.mark.parametrize("limit", [-1, 0])
def test_spend_with_no_limit_counts_nothing(limit):
    redis = FakeRedis()

    assert statuses([lambda: spend(redis, "key", 1_000, limit, 60)] * 2) == [200, 200]
    assert redis.counts == {}
