from uuid import UUID

from fastapi import HTTPException, status
from prepza_common import company_access, http

from app.config.settings import settings
from app.service_auth import service_token

# Companies' answers the API passes on as they are: not found, no credits, not ready, over the
# email limits, paused.
PASSED_ON = {
    status.HTTP_402_PAYMENT_REQUIRED,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_409_CONFLICT,
    status.HTTP_429_TOO_MANY_REQUESTS,
    status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('companies')}"}


async def _get(path: str, params: dict | None = None):
    response = await http.get_client().get(
        f"{settings.companies_url}{path}", params=params, headers=_headers()
    )

    if response.status_code in PASSED_ON:
        raise HTTPException(response.status_code, response.json().get("detail"))

    response.raise_for_status()

    return response.json()


async def access(company_id: UUID, user_id: str) -> dict:
    """What the user may do in the company; a company that's gone is no access."""
    return await company_access.access(
        settings.companies_url, service_token("companies"), company_id, user_id
    )


async def interviews(company_id: UUID, offset: int, limit: int) -> list[dict]:
    path = f"/internal/companies/{company_id}/interviews"

    return await _get(path, {"offset": offset, "limit": limit})


async def interview(company_id: UUID, interview_id: UUID) -> dict:
    """The company's interview; 404 when it isn't the company's."""
    return await _get(f"/internal/companies/{company_id}/interviews/{interview_id}")


async def candidates(company_id: UUID, interview_id: UUID, offset: int, limit: int) -> list[dict]:
    path = f"/internal/companies/{company_id}/interviews/{interview_id}/candidates"

    return await _get(path, {"offset": offset, "limit": limit})


async def candidate(company_id: UUID, interview_id: UUID, invite_id: UUID) -> dict:
    path = f"/internal/companies/{company_id}/interviews/{interview_id}/candidates/{invite_id}"

    return await _get(path)


async def invite(interview_id: UUID, email: str, sender_id: str, name: str | None = None) -> UUID:
    """Invites the candidate as `sender_id` would, and returns the invite's id. Companies'
    refusals (PASSED_ON) raise an HTTPException with its status and reason."""
    response = await http.get_client().post(
        f"{settings.companies_url}/internal/interviews/{interview_id}/invites",
        json={"email": email, "sender_id": sender_id, "name": name},
        headers=_headers(),
    )

    if response.status_code in PASSED_ON:
        raise HTTPException(response.status_code, response.json().get("detail"))

    response.raise_for_status()

    return UUID(response.json()["invite_id"])
