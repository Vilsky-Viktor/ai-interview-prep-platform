from uuid import UUID

from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def use_candidate(company_id: UUID) -> None:
    """Uses one candidate credit; billing's 402 and its message reach the user unchanged."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/companies/{company_id}/candidates/use",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, response.json()["detail"])

    response.raise_for_status()


async def candidate_credits(company_id: UUID) -> int:
    response = await http.get_client().get(
        f"{settings.billing_url}/internal/companies/{company_id}/credits",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()

    return response.json()["candidate_credits"]
