import httpx
from fastapi import HTTPException, status
from prepza_common import http

from app.constants.ats import ATS_TIMEOUT_SECONDS
from app.integrations.errors import KeyRejected

# What an ATS answers a key it refuses: wrong, revoked, expired or missing a permission.
REJECTED = {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


async def send(
    method: str,
    url: str,
    headers: dict,
    unavailable: str,
    params: dict | None = None,
    body: dict | None = None,
) -> httpx.Response:
    """One call to an ATS's API; an ATS that doesn't answer is a 502 with `unavailable` (its
    name's "… didn't answer"), which the caller can retry."""
    try:
        return await http.get_client().request(
            method, url, params=params, json=body, headers=headers, timeout=ATS_TIMEOUT_SECONDS
        )
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, unavailable) from error


def checked(
    response: httpx.Response,
    unavailable: str,
    rejected: set[int] = REJECTED,
    passes_429: bool = False,
) -> httpx.Response:
    """The ATS's answer, once it worked: a refused key raises KeyRejected; something deleted in
    the ATS (a job, a candidate), a 404, as only that is gone, not the key; with `passes_429`, a
    rate limit stays a 429 (a web hook answered so is sent again later); anything else that
    failed is a 502 with `unavailable`."""
    if response.status_code in rejected:
        raise KeyRejected

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    if passes_429 and response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, unavailable)

    if not response.is_success:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, unavailable)

    return response


def json_of(response: httpx.Response) -> dict:
    return response.json() if response.content else {}
