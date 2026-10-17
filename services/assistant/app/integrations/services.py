from contextvars import ContextVar

import httpx
from prepza_common import http
from prepza_common.constants import REFERRAL_COOKIE, VIA_ASSISTANT
from prepza_common.http import bearer

from app.config.settings import settings
from app.constants.tool_calls import (
    ASSISTANT_HEADER,
    REFERRAL_CODE,
    SERVICE_URLS,
    TOOL_TIMEOUT_SECONDS,
)
from app.service_auth import service_token

# For the MCP call being handled when an AI agent signed in with an API key: the key's company
# and id, which companies' X-Assistant header carries (it refuses any other company).
KEY_CLAIMS: ContextVar[dict | None] = ContextVar("key_claims", default=None)


async def get(
    service: str, path: str, query: dict, token: str, language: str, via: str = VIA_ASSISTANT
) -> httpx.Response:
    """A GET to another service's user-facing route as the user, in their language."""
    return await send(service, "GET", path, query, None, token, language, via=via)


async def send(
    service: str,
    method: str,
    path: str,
    query: dict,
    body: dict | None,
    token: str,
    language: str,
    idempotency_key: str | None = None,
    via: str = VIA_ASSISTANT,
    referral: str | None = None,
) -> httpx.Response:
    """A call to another service's user-facing route as the user, in their language: a read, or
    a write the user confirmed. Companies also gets the assistant's signed header naming what it
    came through (`via`: the assistant or an AI app), so it audits it as such."""
    headers = {**bearer(token), "Accept-Language": language}

    if service == "companies":
        headers[ASSISTANT_HEADER] = service_token("companies", via, KEY_CLAIMS.get())

        # The referral link the user came through (their browser's cookie): a company the
        # assistant creates for them counts for the referrer, as one made on the site does.
        if referral and REFERRAL_CODE.fullmatch(referral):
            headers["Cookie"] = f"{REFERRAL_COOKIE}={referral}"

    # A confirmed action's id: a service that takes the header runs it at most once.
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    return await http.get_client().request(
        method,
        getattr(settings, SERVICE_URLS[service]) + path,
        params=query,
        json=body,
        headers=headers,
        timeout=TOOL_TIMEOUT_SECONDS,
    )
