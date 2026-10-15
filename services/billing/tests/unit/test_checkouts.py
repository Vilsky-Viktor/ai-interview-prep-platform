import asyncio

from app.integrations import paddle
from app.services import webhooks
from app.storage import ledger
from tests.unit.paddle_events import completed
from tests.unit.test_internal import AUTH
from tests.unit.test_webhooks import granted  # noqa: F401 (fixture)

URL = "/internal/companies/acme/checkout"


def test_a_checkout_opened_in_the_browser_grants_nothing(granted):  # noqa: F811
    event = completed()
    event["data"]["origin"] = "web"

    asyncio.run(webhooks.handle(event))

    assert granted == []


def test_a_payment_into_a_deleted_company_grants_nothing(granted, monkeypatch):  # noqa: F811
    async def none(owner_type, owner_ids):
        return {}

    monkeypatch.setattr(ledger, "wallets", none)

    asyncio.run(webhooks.handle(completed()))

    assert granted == []


def test_billing_makes_the_checkout_with_whose_wallet_it_pays_into(client, monkeypatch):
    made = []

    async def create(price_id, custom_data):
        made.append((price_id, custom_data))

        return "txn_new"

    monkeypatch.setattr(paddle, "create_transaction", create)

    response = client.post(
        URL, params={"buyer_id": "ann"}, json={"price_id": "pri_topup_50"}, headers=AUTH
    )
    other = client.post(URL, params={"buyer_id": "ann"}, json={"price_id": "pri_x"}, headers=AUTH)

    assert response.json() == {"transaction_id": "txn_new"}
    assert other.status_code == 422
    assert made == [
        ("pri_topup_50", {"owner_type": "company", "owner_id": "acme", "buyer_id": "ann"})
    ]
