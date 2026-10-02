from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def use_generation(user_id: str) -> None:
    """Uses one of the learner's preparations: a pass, the month's free one or a credit.
    Billing's 402 and its message reach the user unchanged."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/users/{user_id}/generations/use",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, response.json()["detail"])

    response.raise_for_status()
