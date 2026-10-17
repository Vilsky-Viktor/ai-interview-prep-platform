from fastapi import HTTPException, status
from prepza_common import http
from prepza_common.http import bearer

from app.config.settings import settings
from app.constants.mcp import VERIFY_KEY_PATH
from app.service_auth import service_token


async def verify(key: str) -> dict | None:
    """The api service's check of a company's API key, as the API checks it, counted against
    the company's API limit: its id, company_id, created_by (the member it acts as) and
    permissions. None for a key that doesn't work; over the limit, the api's 429."""
    response = await http.get_client().post(
        settings.api_url + VERIFY_KEY_PATH,
        json={"key": key},
        headers=bearer(service_token("api")),
    )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return None

    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, response.json()["detail"])

    response.raise_for_status()

    return response.json()
