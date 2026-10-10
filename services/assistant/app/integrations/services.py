import httpx
from prepza_common import http

from app.config.settings import settings
from app.constants.tool_calls import (
    ASSISTANT_HEADER,
    SERVICE_URLS,
    TOOL_TIMEOUT_SECONDS,
    VIA_ASSISTANT,
)
from app.service_auth import service_token


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
) -> httpx.Response:
    """A call to another service's user-facing route as the user, in their language: a read, or
    a write the user confirmed. Companies also gets the assistant's signed header naming what it
    came through (`via`: the assistant or an AI app), so it audits it as such."""
    headers = {"Authorization": f"Bearer {token}", "Accept-Language": language}

    if service == "companies":
        headers[ASSISTANT_HEADER] = service_token("companies", via)

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
