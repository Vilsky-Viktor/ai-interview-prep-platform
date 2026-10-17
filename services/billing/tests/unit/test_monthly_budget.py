"""The AI costs tab's month: its spend against the monthly budget set in Controls."""

import asyncio

import pytest
from prepza_common import memory_cache
from prepza_common.limit_list import LIMITS_KEY

from app.services import ai_costs
from app.storage import ai_costs as ai_costs_storage


class LimitsRedis:
    """Only the hash of the limits edited in Controls."""

    def __init__(self, edited: dict):
        self.edited = edited

    async def hgetall(self, key):
        assert key == LIMITS_KEY

        return self.edited


@pytest.mark.parametrize(
    ("edited", "budget", "share"),
    [({}, 300.0, 0.25), ({"MONTHLY_BUDGET": "150"}, 150.0, 0.5), ({"MONTHLY_BUDGET": "0"}, 0, 0)],
)
def test_the_months_spend_is_a_share_of_the_budget_set_in_controls(
    monkeypatch, edited, budget, share
):
    async def totals(where):
        return 75.0, 10, 0, 0, 0

    monkeypatch.setattr(memory_cache, "_entries", {})
    monkeypatch.setattr(ai_costs_storage, "totals", totals)
    monkeypatch.setattr(ai_costs, "get_redis", lambda: LimitsRedis(edited))

    month = asyncio.run(ai_costs.month_out())

    assert (month.spend, month.budget, month.share) == (75.0, budget, share)
