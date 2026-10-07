import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.constants.ats import (
    ATS_TIMEOUT_SECONDS,
    WORKABLE_API,
    WORKABLE_MAX_PAGES,
    WORKABLE_PAGE,
)

# Workable's answers that mean the key is wrong, revoked, expired or lacks a scope.
REJECTED = {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


class KeyRejected(Exception):
    """Workable refused the key: the connection needs a new one."""


async def _get(subdomain: str, token: str, path: str, params: dict | None = None) -> dict:
    """One call to Workable's API. A refused key raises KeyRejected; anything else that fails
    (down, rate limited, unknown subdomain) is a 502 the company can retry."""
    try:
        response = await http.get_client().get(
            WORKABLE_API.format(subdomain=subdomain) + path,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=ATS_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Workable didn't answer") from error

    if response.status_code in REJECTED:
        raise KeyRejected

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Workable didn't answer")

    return response.json()


async def check(subdomain: str, token: str) -> None:
    """Raises KeyRejected unless the key may read the account's jobs."""
    await _get(subdomain, token, "/jobs", {"limit": 1})


async def jobs(subdomain: str, token: str) -> list[dict]:
    """The account's published jobs, as {id, name}, a page at a time."""
    found: list[dict] = []
    params: dict = {"state": "published", "limit": WORKABLE_PAGE}

    for _ in range(WORKABLE_MAX_PAGES):
        page = await _get(subdomain, token, "/jobs", params)
        found += [{"id": job["shortcode"], "name": job["title"]} for job in page.get("jobs", [])]
        since_id = page.get("paging", {}).get("next")

        if not since_id:
            break

        # Workable's next page is a full address with since_id; only that parameter is kept.
        params = {**params, "since_id": httpx.URL(since_id).params.get("since_id")}

    return found


async def stages(subdomain: str, token: str, job_id: str) -> list[dict]:
    """A job's pipeline stages in order, as {id, name}."""
    page = await _get(subdomain, token, f"/jobs/{job_id}/stages")

    return [{"id": stage["slug"], "name": stage["name"]} for stage in page.get("stages", [])]


async def job(subdomain: str, token: str, job_id: str) -> dict:
    """One job: its title and its description, requirements and benefits (HTML)."""
    found = await _get(subdomain, token, f"/jobs/{job_id}")

    return {
        "name": found.get("title", ""),
        "sections": [found.get(key) or "" for key in ("description", "requirements", "benefits")],
    }
