from uuid import UUID

from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('billing')}"}


async def hold_candidate(company_id: UUID, key: str) -> None:
    """Sets a candidate's credits aside. Billing's 402 and its message reach the user unchanged."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/candidates/hold",
        params={"company_id": str(company_id), "key": key},
        headers=_headers(),
    )

    if response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, response.json()["detail"])

    response.raise_for_status()


async def charge_candidate(key: str) -> None:
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/candidates/charge",
        params={"key": key},
        headers=_headers(),
    )

    response.raise_for_status()


async def release_candidate(key: str) -> None:
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/candidates/release",
        params={"key": key},
        headers=_headers(),
    )

    response.raise_for_status()


async def welcome_company(
    company_id: UUID, owner_email: str, referral: str | None, related: list[str]
) -> None:
    """The welcome credits come once per owner's email; billing keeps only a hash of it. A
    referral code counts unless it's from one of the owner's other companies (`related`)."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/companies/{company_id}/welcome",
        json={"owner_email": owner_email, "referral": referral, "related": related},
        headers=_headers(),
    )

    response.raise_for_status()


async def company_referral(company_id: UUID) -> dict:
    """The company's referral code, its reward, and how many it has earned for."""
    response = await http.get_client().get(
        f"{settings.billing_url}/internal/companies/{company_id}/referral",
        headers=_headers(),
    )

    response.raise_for_status()

    return response.json()


async def company_credits(company_id: UUID) -> dict:
    """The company's available credits, and whether they're running low."""
    response = await http.get_client().get(
        f"{settings.billing_url}/internal/companies/{company_id}/credits",
        headers=_headers(),
    )

    response.raise_for_status()

    return response.json()


async def delete_company(company_id: UUID) -> None:
    """The company's wallet and history; safe to repeat."""
    response = await http.get_client().delete(
        f"{settings.billing_url}/internal/companies/{company_id}",
        headers=_headers(),
    )

    response.raise_for_status()


async def companies_credits(company_ids: list[UUID]) -> dict[str, dict]:
    """Each company's balance, by id."""
    response = await http.get_client().post(
        f"{settings.billing_url}/internal/companies/credits",
        json={"owner_ids": [str(company_id) for company_id in company_ids]},
        headers=_headers(),
    )

    response.raise_for_status()

    return response.json()
