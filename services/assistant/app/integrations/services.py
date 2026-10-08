import httpx
from prepza_common import http

from app.config.settings import settings
from app.constants.tool_calls import ASSISTANT_HEADER, SERVICE_URLS, TOOL_TIMEOUT_SECONDS
from app.service_auth import service_token


async def get(service: str, path: str, query: dict, token: str, language: str) -> httpx.Response:
    """A GET to another service's user-facing route as the user, in their language. Companies
    also gets the assistant's signed header, so it audits the read as the assistant's."""
    headers = {"Authorization": f"Bearer {token}", "Accept-Language": language}

    if service == "companies":
        headers[ASSISTANT_HEADER] = service_token("companies")

    return await http.get_client().get(
        getattr(settings, SERVICE_URLS[service]) + path,
        params=query,
        headers=headers,
        timeout=TOOL_TIMEOUT_SECONDS,
    )
