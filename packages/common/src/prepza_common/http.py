from collections.abc import Collection
from functools import cache

import httpx
from fastapi import HTTPException
from prepza_common.constants import HTTP_RETRIES, HTTP_TIMEOUT_SECONDS


@cache
def get_client() -> httpx.AsyncClient:
    """One client per process, so calls to other services reuse their connections."""
    return httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=HTTP_RETRIES), timeout=HTTP_TIMEOUT_SECONDS
    )


def bearer(token: str) -> dict[str, str]:
    """The Authorization header carrying `token`: another service's, a user's, or a provider's
    key."""
    return {"Authorization": f"Bearer {token}"}


def passed_on(response: httpx.Response, codes: Collection[int] | None = None) -> httpx.Response:
    """Another service's answer, once it worked. Its refusals in `codes` (any refusal, without
    them) reach the client unchanged, status and reason; another failure raises."""
    refused = response.is_error if codes is None else response.status_code in codes

    if refused:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = None

        raise HTTPException(response.status_code, detail)

    if response.is_error:
        response.raise_for_status()

    return response
