import asyncio
from types import SimpleNamespace

import pytest
from prepza_common.notifications import notification

from app.integrations import paddle
from app.services import auto_top_ups, referrals, topups, webhooks
from app.storage import auto_top_ups as auto_top_ups_storage
from app.storage import purchases
from app.storage import referrals as referrals_storage
from tests.unit.paddle_events import completed


@pytest.fixture
def notified(monkeypatch):
    sent = []

    async def fake_publish(event):
        sent.append(event)

    for module in (referrals, topups, auto_top_ups):
        monkeypatch.setattr(module, "publish_quietly", fake_publish)

    return sent


@pytest.mark.parametrize(
    "owner_type, link",
    [("user", "/settings/referral"), ("company", "/company/bob/referrals")],
)
def test_a_rewarded_referrer_is_told_with_the_reward(monkeypatch, notified, owner_type, link):
    async def rewarded(owner_type, owner_id):
        return "bob"

    monkeypatch.setattr(referrals_storage, "reward", rewarded)

    asyncio.run(referrals.reward_after_top_up(owner_type, "ann", 5_000))

    credits = {"user": 200, "company": 500}[owner_type]
    assert notified == [notification(owner_type, "bob", "referral_rewarded", link, credits=credits)]


@pytest.fixture
def granted(monkeypatch):
    async def fake_grant(*args):
        return True

    async def no_referral(owner_type, owner_id):
        return None

    async def owner(subscription_id):
        return ("company", "acme")

    monkeypatch.setattr(purchases, "grant", fake_grant)
    monkeypatch.setattr(referrals_storage, "reward", no_referral)
    monkeypatch.setattr(auto_top_ups_storage, "owner_of", owner)


def test_an_automatic_top_up_tells_the_owner_the_credits_it_added(granted, notified):
    event = completed()
    event["data"]["subscription_id"] = "sub_01"

    asyncio.run(webhooks.handle(event))

    assert notified == [
        notification("company", "acme", "auto_top_up_charged", "/top-up", credits=1_000)
    ]


def test_a_top_up_bought_by_hand_tells_nobody(granted, notified):
    asyncio.run(webhooks.handle(completed()))

    assert notified == []


def test_a_declined_automatic_charge_tells_the_owner(monkeypatch, notified):
    async def claimed(owner_type, owner_id, now):
        return SimpleNamespace(subscription_id="sub_01", product="topup_10")

    async def declined(subscription_id, price_id):
        raise RuntimeError("declined")

    monkeypatch.setattr(auto_top_ups_storage, "claim_charge", claimed)
    monkeypatch.setattr(paddle, "charge", declined)

    asyncio.run(auto_top_ups.check("user", "ann"))

    assert notified == [notification("user", "ann", "auto_top_up_failed", "/top-up")]
