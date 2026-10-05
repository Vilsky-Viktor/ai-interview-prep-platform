import asyncio

import pytest

from app.services import adjustments, webhooks
from app.storage import ledger, purchases


def adjustment(action="refund", status="approved", total="1000", adjustment_id="adj_01"):
    return {
        "event_type": "adjustment.updated",
        "data": {
            "id": adjustment_id,
            "action": action,
            "status": status,
            "transaction_id": "txn_01",
            "totals": {"total": total, "currency_code": "USD"},
        },
    }


@pytest.fixture
def moved(monkeypatch):
    calls = []

    async def bought(transaction_id):
        # $10 paid for 1,000 credits.
        return ("company", "acme", 1_000, "1000")

    async def adjust(owner_type, owner_id, amount, key, reason):
        calls.append((owner_id, amount, key, reason))

    monkeypatch.setattr(purchases, "for_transaction", bought)
    monkeypatch.setattr(ledger, "adjust", adjust)

    return calls


def test_an_approved_refund_takes_the_credits_back(moved):
    asyncio.run(webhooks.handle(adjustment()))

    assert moved == [("acme", -1_000, "adjustment:adj_01", "refund")]


def test_a_partial_refund_takes_back_its_share(moved):
    asyncio.run(webhooks.handle(adjustment(total="250")))

    assert moved == [("acme", -250, "adjustment:adj_01", "refund")]


def test_a_chargeback_takes_back_and_its_reversal_returns(moved):
    asyncio.run(webhooks.handle(adjustment(action="chargeback", adjustment_id="adj_cb")))
    asyncio.run(webhooks.handle(adjustment(action="chargeback_reverse", adjustment_id="adj_rv")))

    assert [amount for _, amount, _, _ in moved] == [-1_000, 1_000]


@pytest.mark.parametrize(
    "event",
    [
        adjustment(status="pending_approval"),
        adjustment(status="rejected"),
        adjustment(action="chargeback_warning"),
        adjustment(action="credit"),
    ],
)
def test_nothing_moves_for_pending_rejected_or_other_adjustments(moved, event):
    asyncio.run(webhooks.handle(event))

    assert moved == []


def test_never_more_than_was_paid():
    assert adjustments.share(1_000, "5000", "1000") == 1_000
    assert adjustments.share(26_250, "12500", "25000") == 13_125
