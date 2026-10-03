import uuid
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException

from app.config.settings import settings
from app.constants.credits import KIT_CREDITS, Reason
from app.constants.products import AUTO_TOP_UP_COOLDOWN, OwnerType
from app.helpers.credits import credits_for
from app.integrations import paddle
from app.schemas.billing import AutoTopUpIn
from app.services import auto_top_ups
from app.services.topups import handle_completed
from app.storage import auto_top_ups as rows
from app.storage import ledger

USER = OwnerType.USER


@pytest.fixture
def paddle_calls(monkeypatch):
    """Paddle's API, faked: what was charged and cancelled."""
    calls = []

    async def charge(subscription_id, price_id):
        calls.append(("charge", subscription_id, price_id))

    async def cancel(subscription_id):
        calls.append(("cancel", subscription_id))

    monkeypatch.setattr(paddle, "charge", charge)
    monkeypatch.setattr(paddle, "cancel", cancel)
    monkeypatch.setattr(settings, "paddle_api_key", "key")
    monkeypatch.setattr(settings, "paddle_price_auto_top_up", "pri_plan")
    monkeypatch.setattr(settings, "paddle_price_topup_25", "pri_25")

    return calls


def checkout_data(owner_id, buyer_id):
    return {"owner_type": USER, "owner_id": owner_id, "buyer_id": buyer_id, "auto_top_up": "1"}


def test_turning_on_waits_for_the_checkout_then_refills_under_the_threshold_once(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    sub = f"sub_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await ledger.welcome_user(ann, f"{ann}@example.com")
        waiting = await auto_top_ups.turn_on(
            USER, ann, AutoTopUpIn(product="topup_25", threshold=300), ann
        )
        # Someone else's checkout can't start it; the owner's does, once.
        await auto_top_ups.start(checkout_data(ann, "mallory"), "sub_other")
        await auto_top_ups.start(checkout_data(ann, ann), sub)
        await auto_top_ups.start(checkout_data(ann, ann), sub)
        started = await auto_top_ups.out(USER, ann)
        # 500 available: above 300, nothing is charged. A kit leaves 0: one charge, however
        # often it's checked within the cooldown.
        await auto_top_ups.check(USER, ann)
        await ledger.reserve(USER, ann, KIT_CREDITS, f"kit:{uuid.uuid4()}", Reason.KIT)
        await auto_top_ups.check(USER, ann)
        await auto_top_ups.check(USER, ann)
        later = await rows.claim_charge(USER, ann, datetime.now(UTC) + AUTO_TOP_UP_COOLDOWN * 2)

        return waiting, started, later

    waiting, started, later = run(scenario())

    assert waiting.checkout.price_id == "pri_plan" and not waiting.on and waiting.waiting
    assert waiting.checkout.custom_data == checkout_data(ann, ann)
    assert started.on and started.product == "topup_25" and started.threshold == 300
    assert paddle_calls == [("cancel", "sub_other"), ("charge", sub, "pri_25")]
    assert later is not None


def test_turning_off_cancels_the_subscription_and_choices_are_checked(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    sub = f"sub_{uuid.uuid4().hex[:12]}"

    async def scenario():
        await auto_top_ups.turn_on(USER, ann, AutoTopUpIn(product="topup_25", threshold=100), ann)
        await auto_top_ups.start(checkout_data(ann, ann), sub)
        await auto_top_ups.turn_off(USER, ann)
        refused = []

        for body in (
            AutoTopUpIn(product="topup_25", threshold=123),
            AutoTopUpIn(product="topup_50", threshold=100),
        ):
            try:
                await auto_top_ups.turn_on(USER, ann, body, ann)
            except HTTPException as error:
                refused.append(error.status_code)

        return await auto_top_ups.out(USER, ann), refused

    after, refused = run(scenario())

    assert not after.on and not after.waiting
    assert paddle_calls == [("cancel", sub)]
    assert refused == [422, 422]


def test_an_automatic_charge_credits_the_wallet_its_subscription_belongs_to(run, paddle_calls):
    ann = f"user-{uuid.uuid4()}"
    sub = f"sub_{uuid.uuid4().hex[:12]}"

    def transaction(price_id, custom_data):
        return {
            "id": f"txn_{uuid.uuid4().hex[:12]}",
            "subscription_id": sub,
            "currency_code": "USD",
            "custom_data": custom_data,
            "items": [{"price": {"id": price_id}, "quantity": 1}],
            "details": {"totals": {"grand_total": "2500"}},
        }

    async def scenario():
        await auto_top_ups.turn_on(USER, ann, AutoTopUpIn(product="topup_25", threshold=100), ann)
        # The $0 checkout starts it and buys nothing; the charge carries no custom data.
        await handle_completed(transaction("pri_plan", checkout_data(ann, ann)))
        opened = await ledger.wallet(USER, ann)
        await handle_completed(transaction("pri_25", None))

        return opened.balance, (await ledger.wallet(USER, ann)).balance

    opened, after = run(scenario())

    assert opened == 0
    assert after == credits_for(2_500)
