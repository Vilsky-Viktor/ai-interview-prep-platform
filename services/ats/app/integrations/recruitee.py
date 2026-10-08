import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.constants.ats import ATS_TIMEOUT_SECONDS, RECRUITEE_API, RECRUITEE_OPEN_JOBS
from app.integrations.errors import KeyRejected

# The credentials this client takes: the company (its subdomain) and a personal API token, which
# acts as the person who made it.
KEYS = ("company", "token")
# Recruitee's answers that mean the token is wrong, revoked, or its person can't see that.
REJECTED = {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


async def _call(
    method: str, company: str, token: str, path: str, params=None, body=None, rejected=REJECTED
) -> dict:
    try:
        response = await http.get_client().request(
            method,
            RECRUITEE_API.format(company=company) + path,
            params=params,
            json=body,
            headers={"Authorization": f"Bearer {token}"},
            timeout=ATS_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Recruitee didn't answer") from error

    if response.status_code in rejected:
        raise KeyRejected

    # Something deleted in Recruitee (a job, a candidate): only that is gone, not the key.
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    if not response.is_success:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Recruitee didn't answer")

    return response.json() if response.content else {}


async def check(company: str, token: str) -> None:
    """Raises KeyRejected unless the token may read the company's jobs. A company that isn't
    there answers 404: the address is wrong, as good as a refused key."""
    rejected = REJECTED | {status.HTTP_404_NOT_FOUND}
    await _call("GET", company, token, "/offers", {"limit": 1}, rejected=rejected)


async def jobs(company: str, token: str) -> list[dict]:
    """The jobs still hiring (published, or internal only), as {id, name}."""
    found = await _call("GET", company, token, "/offers", {"statuses[]": RECRUITEE_OPEN_JOBS})

    return [
        {"id": str(offer["id"]), "name": offer.get("title", "")}
        for offer in found.get("offers", [])
        if offer.get("kind", "job") == "job"
    ]


async def _offer(company: str, token: str, job_id: str) -> dict:
    return (await _call("GET", company, token, f"/offers/{job_id}")).get("offer") or {}


async def stages(company: str, token: str, job_id: str) -> list[dict]:
    """A job's stages in its pipeline's order, as {id, name}."""
    offer = await _offer(company, token, job_id)
    found = (offer.get("pipeline_template") or {}).get("stages", [])
    found = sorted(found, key=lambda stage: stage.get("position") or 0)

    return [{"id": str(stage["id"]), "name": stage.get("name", "")} for stage in found]


async def job(company: str, token: str, job_id: str) -> dict:
    """A job's title and its text (HTML): the description and the requirements."""
    offer = await _offer(company, token, job_id)

    return {
        "name": offer.get("title", ""),
        "sections": [offer.get("description") or "", offer.get("requirements") or ""],
    }


async def comment(
    company: str, token: str, candidate_id: str, member: str | None, text: str
) -> None:
    """A note on the candidate in Recruitee, as the person whose token it is."""
    body = {"note": {"body": text, "visibility": {"level": "public"}}}
    await _call("POST", company, token, f"/candidates/{candidate_id}/notes", body=body)
