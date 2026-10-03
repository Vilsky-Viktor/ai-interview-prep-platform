import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('billing')}"}


async def catalog() -> dict | None:
    """Billing's public prices; None when billing can't be reached, so help still answers."""
    try:
        response = await http.get_client().get(f"{settings.billing_url}/catalog")
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    return response.json()


async def available_credits(user_id: str) -> int:
    response = await http.get_client().get(
        f"{settings.billing_url}/internal/users/{user_id}/credits", headers=_headers()
    )

    response.raise_for_status()

    return response.json()["available"]


async def charge_chat_turn(user_id: str, key: str) -> None:
    """A tutor turn after the free ones; safe to repeat with the same key."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/chat-turns",
        json={"owner_id": user_id, "key": key},
        headers=_headers(),
    )

    response.raise_for_status()


async def charge_certificate(user_id: str, key: str, topic_title: str, author_id: str) -> None:
    """A certificate on someone else's public kit; its author gets a share. Billing's 402 and its
    message reach the user unchanged."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/certificates",
        json={"owner_id": user_id, "key": key, "note": topic_title, "author_id": author_id},
        headers=_headers(),
    )

    if response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, response.json()["detail"])

    response.raise_for_status()
