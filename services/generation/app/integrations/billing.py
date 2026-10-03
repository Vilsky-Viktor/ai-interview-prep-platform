from uuid import UUID

from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('billing')}"}


async def hold_kit(user_id: str, generation_id: UUID) -> None:
    """Sets a kit's credits aside. Billing's 402 and its message reach the user unchanged."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/kits/{generation_id}/hold",
        params={"user_id": user_id},
        headers=_headers(),
    )

    if response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, response.json()["detail"])

    response.raise_for_status()


async def charge_kit(generation_id: UUID) -> None:
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/kits/{generation_id}/charge",
        headers=_headers(),
    )

    response.raise_for_status()


async def release_kit(generation_id: UUID) -> None:
    """Gives the credits back. A kit that was never held, or already charged, is left as it is."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/kits/{generation_id}/release",
        headers=_headers(),
    )

    response.raise_for_status()
