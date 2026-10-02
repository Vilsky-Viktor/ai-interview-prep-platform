from functools import cache

import httpx
from prepza_common.constants import HTTP_RETRIES, HTTP_TIMEOUT_SECONDS


@cache
def get_client() -> httpx.AsyncClient:
    """One client per process, so calls to other services reuse their connections."""
    return httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=HTTP_RETRIES), timeout=HTTP_TIMEOUT_SECONDS
    )
