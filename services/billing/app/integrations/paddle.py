from prepza_common import http

from app.config.settings import settings
from app.constants.products import PADDLE_API


def _url(path: str) -> str:
    return f"{PADDLE_API[settings.paddle_environment]}{path}"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.paddle_api_key}"}


async def charge(subscription_id: str, price_id: str) -> None:
    """Bills one top-up to the subscription's saved card now. Its transaction.completed webhook
    adds the credits; a declined card raises and changes nothing."""
    response = await http.get_client().post(
        _url(f"/subscriptions/{subscription_id}/charge"),
        json={
            "effective_from": "immediately",
            "items": [{"price_id": price_id, "quantity": 1}],
            "on_payment_failure": "prevent_change",
        },
        headers=_headers(),
    )

    response.raise_for_status()


async def cancel(subscription_id: str) -> None:
    """Ends the subscription at once, so the card isn't kept for us."""
    response = await http.get_client().post(
        _url(f"/subscriptions/{subscription_id}/cancel"),
        json={"effective_from": "immediately"},
        headers=_headers(),
    )

    response.raise_for_status()


async def subscription_status(subscription_id: str) -> str:
    """The subscription's status now: active, canceled and so on."""
    response = await http.get_client().get(
        _url(f"/subscriptions/{subscription_id}"), headers=_headers()
    )

    response.raise_for_status()

    return response.json()["data"]["status"]


async def invoice_url(transaction_id: str) -> str:
    """A temporary link to the transaction's invoice PDF."""
    response = await http.get_client().get(
        _url(f"/transactions/{transaction_id}/invoice"), headers=_headers()
    )

    response.raise_for_status()

    return response.json()["data"]["url"]
