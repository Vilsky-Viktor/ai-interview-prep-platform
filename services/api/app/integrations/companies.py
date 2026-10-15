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
    status.HTTP_422_UNPROCESSABLE_CONTENT,
    status.HTTP_429_TOO_MANY_REQUESTS,
    status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _headers() -> dict:
    return {"Authorization": f"Bearer {service_token('companies')}"}


async def _call(method: str, path: str, params: dict | None = None, body: dict | None = None):
    """Companies' answer, its refusals (PASSED_ON) raised with their status and reason; None
    when it has no body."""
    response = await http.get_client().request(
        method, f"{settings.companies_url}{path}", params=params, json=body, headers=_headers()
    )

    if response.status_code in PASSED_ON:
        raise HTTPException(response.status_code, response.json().get("detail"))

    response.raise_for_status()

    return response.json() if response.content else None


async def _get(path: str, params: dict | None = None):
    return await _call("GET", path, params)


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


async def invite(
    interview_id: UUID,
    email: str,
    sender_id: str,
    name: str | None = None,
    return_url: str | None = None,
    sign_in: bool = True,
    theme: str | None = None,
) -> UUID:
    """Invites the candidate as `sender_id` would, and returns the invite's id. Companies'
    refusals (PASSED_ON) raise an HTTPException with its status and reason."""
    response = await http.get_client().post(
        f"{settings.companies_url}/internal/interviews/{interview_id}/invites",
        json={
            "email": email,
            "sender_id": sender_id,
            "name": name,
            "return_url": return_url,
            "sign_in": sign_in,
            "theme": theme,
        },
        headers=_headers(),
    )

    if response.status_code in PASSED_ON:
        raise HTTPException(response.status_code, response.json().get("detail"))

    response.raise_for_status()

    return UUID(response.json()["invite_id"])


def _candidate_path(company_id: UUID, interview_id: UUID, invite_id: UUID) -> str:
    return f"/internal/companies/{company_id}/interviews/{interview_id}/candidates/{invite_id}"


async def create_interview(
    company_id: UUID, text: str, generate_in: str | None, user_id: str
) -> dict:
    """Starts making an interview from a job description, as `user_id`, the key's creator."""
    return await _call(
        "POST",
        f"/internal/companies/{company_id}/interviews",
        {"user_id": user_id},
        {"text": text, "generate_in": generate_in},
    )


async def remove_candidate(
    company_id: UUID, interview_id: UUID, invite_id: UUID, user_id: str
) -> None:
    path = _candidate_path(company_id, interview_id, invite_id)
    await _call("DELETE", path, {"user_id": user_id})


async def rename_candidate(
    company_id: UUID, interview_id: UUID, invite_id: UUID, name: str
) -> None:
    path = _candidate_path(company_id, interview_id, invite_id)
    await _call("PATCH", f"{path}/name", body={"name": name})


async def set_extra_time(
    company_id: UUID, interview_id: UUID, invite_id: UUID, extra_time: int, user_id: str
) -> None:
    path = _candidate_path(company_id, interview_id, invite_id)
    await _call("PUT", f"{path}/extra-time", {"user_id": user_id}, {"extra_time": extra_time})


async def resend(company_id: UUID, interview_id: UUID, invite_id: UUID, user_id: str) -> None:
    path = _candidate_path(company_id, interview_id, invite_id)
    await _call("POST", f"{path}/resend", {"user_id": user_id})


async def find_candidates(company_id: UUID, email: str) -> list[dict]:
    """The company's candidates invited with this email: their interview and candidate ids."""
    return await _get(f"/internal/companies/{company_id}/candidates", {"email": email})


async def credits(company_id: UUID) -> dict:
    return await _get(f"/internal/companies/{company_id}/credits")
