import time

import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.constants.ats import (
    ATS_TIMEOUT_SECONDS,
    GREENHOUSE_API,
    GREENHOUSE_MAX_PAGES,
    GREENHOUSE_PAGE,
    GREENHOUSE_TOKEN_MARGIN_SECONDS,
    GREENHOUSE_TOKEN_URL,
)
from app.integrations.errors import KeyRejected

# Greenhouse's answers that mean the credential is wrong, revoked or lacks a permission.
REJECTED = {status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}
# Access tokens by client id, with when each stops being used: they last about an hour.
_tokens: dict[str, tuple[str, float]] = {}


def _failed() -> HTTPException:
    return HTTPException(status.HTTP_502_BAD_GATEWAY, "Greenhouse didn't answer")


async def _token(client_id: str, client_secret: str, fresh: bool = False) -> str:
    """An access token for the credential (client credentials grant), kept until shortly before
    it expires."""
    kept = _tokens.get(client_id)

    if kept and not fresh and kept[1] > time.monotonic():
        return kept[0]

    try:
        response = await http.get_client().post(
            GREENHOUSE_TOKEN_URL,
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=ATS_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as error:
        raise _failed() from error

    if response.status_code in REJECTED:
        raise KeyRejected

    if not response.is_success:
        raise _failed()

    body = response.json()
    expires = time.monotonic() + body.get("expires_in", 3600) - GREENHOUSE_TOKEN_MARGIN_SECONDS
    _tokens[client_id] = (body["access_token"], expires)

    return body["access_token"]


async def _call(
    method: str,
    client_id: str,
    client_secret: str,
    url: str,
    params: dict | None = None,
    body: dict | None = None,
) -> httpx.Response:
    """One call to the Harvest API; a 401 renews the token once (it may have expired early)."""
    for fresh in (False, True):
        token = await _token(client_id, client_secret, fresh)

        try:
            response = await http.get_client().request(
                method,
                url,
                params=params,
                json=body,
                headers={"Authorization": f"Bearer {token}"},
                timeout=ATS_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError as error:
            raise _failed() from error

        if response.status_code != status.HTTP_401_UNAUTHORIZED:
            break

    if response.status_code in REJECTED:
        raise KeyRejected

    if not response.is_success:
        raise _failed()

    return response


def _items(response: httpx.Response) -> list[dict]:
    """A list answer's items, whether the list comes bare or under "data"."""
    body = response.json() if response.content else []

    return body if isinstance(body, list) else body.get("data", [])


async def _list(client_id: str, client_secret: str, path: str, params: dict) -> list[dict]:
    """Every item of a list endpoint, following its next page (the Link header)."""
    found: list[dict] = []
    url: str | None = GREENHOUSE_API + path
    query: dict | None = {**params, "per_page": GREENHOUSE_PAGE}

    for _ in range(GREENHOUSE_MAX_PAGES):
        response = await _call("GET", client_id, client_secret, url, query)
        found += _items(response)
        url = response.links.get("next", {}).get("url")
        # The next page's address carries its own query.
        query = None

        if not url:
            break

    return found


async def check(client_id: str, client_secret: str) -> None:
    """Raises KeyRejected unless the credential may read jobs."""
    await _call("GET", client_id, client_secret, GREENHOUSE_API + "/jobs", {"per_page": 1})


async def jobs(client_id: str, client_secret: str) -> list[dict]:
    """The open jobs, as {id, name}."""
    found = await _list(client_id, client_secret, "/jobs", {"status": "open"})

    return [{"id": str(job["id"]), "name": job.get("name", "")} for job in found]


async def stages(client_id: str, client_secret: str, job_id: str) -> list[dict]:
    """A job's interview stages in order, as {id, name}."""
    found = await _list(client_id, client_secret, "/job_interview_stages", {"job_ids": job_id})

    return [{"id": str(stage["id"]), "name": stage.get("name", "")} for stage in found]


async def job(client_id: str, client_secret: str, job_id: str) -> dict:
    """A job's name and its job posts' text (HTML)."""
    found = await _list(client_id, client_secret, "/jobs", {"ids": job_id})
    posts = await _list(client_id, client_secret, "/job_posts", {"job_ids": job_id})

    return {
        "name": found[0].get("name", "") if found else "",
        "sections": [post.get("content") or "" for post in posts],
    }


async def comment(
    client_id: str, client_secret: str, candidate_id: str, member: str | None, text: str
) -> None:
    """A note on the candidate's activity feed. `candidate_id` is "<candidate>:<application>"
    as the web hook gave them."""
    candidate, _, application = candidate_id.partition(":")
    body = {
        "candidate_id": int(candidate),
        "body": text,
        "note_type": "NOTE",
        "visibility": "public",
    }

    if application:
        body["application_id"] = int(application)

    if member:
        body["user_id"] = int(member)

    await _call("POST", client_id, client_secret, GREENHOUSE_API + "/notes", body=body)
