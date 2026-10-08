import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.constants.ats import ATS_TIMEOUT_SECONDS, BREEZY_API, BREEZY_STATUS_UPDATED
from app.integrations.errors import KeyRejected

# The credentials this client takes: the company and a personal API key, which acts as the
# person who made it (a connection also keeps its web hook's id and secret).
KEYS = ("company", "token")
# Breezy's answers that mean the key is wrong, or its person left the company.
REJECTED = {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


async def _call(method: str, token: str, path: str, params=None, body=None):
    try:
        response = await http.get_client().request(
            method,
            BREEZY_API + path,
            params=params,
            json=body,
            headers={"Authorization": token},
            timeout=ATS_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Breezy HR didn't answer") from error

    if response.status_code in REJECTED:
        raise KeyRejected

    # Something deleted in Breezy HR (a job, a candidate): only that is gone, not the key.
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    if not response.is_success:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Breezy HR didn't answer")

    return response.json() if response.content else {}


async def company(token: str) -> dict | None:
    """The first company the key's person belongs to, as {id, name}; None when there's none."""
    found = await _call("GET", token, "/companies")

    return {"id": found[0]["_id"], "name": found[0].get("name", "")} if found else None


async def check(company: str, token: str) -> None:
    """Raises KeyRejected unless the key may read the company's positions."""
    await _call("GET", token, f"/company/{company}/positions", {"state": "published"})


async def jobs(company: str, token: str) -> list[dict]:
    """The published positions, as {id, name}."""
    found = await _call("GET", token, f"/company/{company}/positions", {"state": "published"})

    return [{"id": position["_id"], "name": position.get("name", "")} for position in found]


async def _position(company: str, token: str, job_id: str) -> dict:
    return await _call("GET", token, f"/company/{company}/position/{job_id}")


async def stages(company: str, token: str, job_id: str) -> list[dict]:
    """A position's stages, in its pipeline's order, as {id, name}."""
    position = await _position(company, token, job_id)

    if not position.get("pipeline_id"):
        return []

    pipeline = await _call("GET", token, f"/company/{company}/pipeline/{position['pipeline_id']}")

    return [
        {"id": stage["id"], "name": stage.get("name", "")} for stage in pipeline.get("pipeline", [])
    ]


async def job(company: str, token: str, job_id: str) -> dict:
    """A position's name and its description (HTML)."""
    position = await _position(company, token, job_id)

    return {"name": position.get("name", ""), "sections": [position.get("description") or ""]}


async def comment(
    company: str, token: str, candidate_id: str, member: str | None, text: str
) -> None:
    """An internal note on the candidate's activity in the position, as the key's person.
    `candidate_id` is "<position>:<candidate>", as the web hook gave them."""
    position, _, candidate = candidate_id.partition(":")
    path = f"/company/{company}/position/{position}/candidate/{candidate}/stream"
    await _call("POST", token, path, body={"body": text})


async def subscribe(company: str, token: str, url: str) -> tuple[str, str]:
    """Asks Breezy to send the company's stage changes to `url`: the web hook's id and its
    signing secret, which Breezy gives only now."""
    body = {"url": url, "description": "prepza", "events": [BREEZY_STATUS_UPDATED]}
    created = await _call("POST", token, f"/company/{company}/webhook_endpoints", body=body)

    return created["id"], created["secret"]


async def unsubscribe(company: str, token: str, endpoint_id: str) -> None:
    await _call("DELETE", token, f"/company/{company}/webhook_endpoint/{endpoint_id}")
