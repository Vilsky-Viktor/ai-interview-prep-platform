from uuid import UUID

from fastapi import HTTPException, status
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token

# Companies' refusals of an invite that the ATS flow tells apart: no credits, limits, the
# pause, the interview gone, or not ready yet.
INVITE_REFUSALS = {
    status.HTTP_402_PAYMENT_REQUIRED,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_409_CONFLICT,
    status.HTTP_429_TOO_MANY_REQUESTS,
    status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('companies')}"}


async def access(company_id: UUID, user_id: str) -> dict:
    """What the user may do in the company: {"member": bool, "editor": bool}. A company that
    doesn't exist is one they aren't a member of."""
    response = await http.get_client().get(
        f"{settings.companies_url}/internal/companies/{company_id}/access",
        params={"user_id": user_id},
        headers=_headers(),
    )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        return {"member": False, "editor": False}

    response.raise_for_status()

    return response.json()


async def interviews(ids) -> dict[UUID, dict]:
    """The interviews that exist among `ids`, by id: each with its company_id, title, and
    whether its questions are ready."""
    if not ids:
        return {}

    response = await http.get_client().get(
        f"{settings.companies_url}/internal/interviews",
        params={"ids": [str(item) for item in ids]},
        headers=_headers(),
    )

    response.raise_for_status()

    return {UUID(item["id"]): item for item in response.json()}


async def invite(interview_id: UUID, email: str, sender_id: str) -> UUID:
    """Invites the candidate to the interview as `sender_id` would, and returns the invite's id.
    A refusal raises an HTTPException with companies' status (INVITE_REFUSALS)."""
    response = await http.get_client().post(
        f"{settings.companies_url}/internal/interviews/{interview_id}/invites",
        json={"email": email, "sender_id": sender_id},
        headers=_headers(),
    )

    if response.status_code in INVITE_REFUSALS:
        raise HTTPException(response.status_code)

    response.raise_for_status()

    return UUID(response.json()["invite_id"])
