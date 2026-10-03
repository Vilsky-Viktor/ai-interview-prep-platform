import asyncio
import time

import pytest

from app.constants.products import WEBHOOK_TOLERANCE_SECONDS
from app.helpers.paddle import signature_valid
from app.services import webhooks
from app.storage import purchases, referrals
from tests.unit.paddle_events import SECRET, completed, signed


def test_a_signature_from_paddle_is_valid():
    body, header = signed(completed())

    assert signature_valid(header, body, SECRET, time.time(), WEBHOOK_TOLERANCE_SECONDS)


@pytest.mark.parametrize(
    "case", ["wrong secret", "old", "tampered body", "no secret configured", "garbage header"]
)
def test_other_signatures_are_refused(case):
    body, header = signed(completed(), secret="other" if case == "wrong secret" else SECRET)
    secret = "" if case == "no secret configured" else SECRET
    now = time.time() + (WEBHOOK_TOLERANCE_SECONDS + 1 if case == "old" else 0)

    if case == "tampered body":
        body = body.replace(b"acme", b"evil")

    if case == "garbage header":
        header = "nonsense"

    assert not signature_valid(header, body, secret, now, WEBHOOK_TOLERANCE_SECONDS)


@pytest.fixture
def granted(monkeypatch):
    calls = []

    async def fake_grant(
        owner_type,
        owner_id,
        credits,
        quantity,
        transaction_id,
        product,
        buyer_id,
        total,
        currency,
        now,
    ):
        calls.append((transaction_id, product, quantity, credits, owner_id, buyer_id))

        return True

    async def no_referral(owner_type, owner_id):
        return None

    monkeypatch.setattr(purchases, "grant", fake_grant)
    monkeypatch.setattr(referrals, "reward", no_referral)

    return calls


def test_a_completed_transaction_grants_what_its_prices_bought(granted):
    asyncio.run(webhooks.handle(completed(quantity=2)))

    assert granted == [("txn_01", "topup_10", 2, 2_000, "acme", "ann")]


def test_a_custom_amount_buys_its_dollars_in_credits_with_the_bonus(granted):
    asyncio.run(webhooks.handle(completed(price_id="pri_topup_custom", quantity=120)))

    # $120 is over $100, so it gets the 2% bonus.
    assert granted == [("txn_01", "topup_custom", 120, 12_240, "acme", "ann")]


@pytest.mark.parametrize(
    "event",
    [
        completed(price_id="pri_unknown"),
        {**completed(), "event_type": "transaction.created"},
        completed(owner_id=None),
    ],
    ids=["unknown price", "other event", "no owner"],
)
def test_anything_else_grants_nothing(granted, event):
    asyncio.run(webhooks.handle(event))

    assert granted == []


def test_the_webhook_route_checks_the_signature(client, granted):
    body, header = signed(completed())

    ok = client.post("/webhooks/paddle", content=body, headers={"Paddle-Signature": header})
    forged = client.post(
        "/webhooks/paddle", content=body, headers={"Paddle-Signature": header + "0"}
    )

    assert ok.status_code == 200
    assert forged.status_code == 401
    assert len(granted) == 1


def test_the_catalog_lists_every_product_and_which_are_on_sale(client):
    products = client.get("/catalog").json()["products"]

    assert {product["key"]: product["price_id"] for product in products}[
        "topup_10"
    ] == "pri_topup_10"
    assert products[1]["price_id"] is None
