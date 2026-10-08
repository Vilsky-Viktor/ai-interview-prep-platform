import httpx
from fastapi import HTTPException, status

from app.constants.chat import CHAT_FAILED, COMPANY_NOT_FOUND
from app.constants.welcome import WELCOME_LIMIT
from app.integrations import services


async def user_companies(token: str, language: str) -> frozenset[str]:
    """The ids of the companies the user is a member of, as companies lists them for their own
    token; a 503 when it doesn't answer."""
    try:
        response = await services.get(
            "companies", "/companies", {"limit": WELCOME_LIMIT}, token, language
        )
    except httpx.HTTPError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, CHAT_FAILED) from None

    if not response.is_success:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, CHAT_FAILED)

    return frozenset(str(company["id"]) for company in response.json())


def require_company(company_id, companies: frozenset[str]) -> None:
    """Refuses (404) a company that isn't one of the user's, before anything is called with it."""
    if company_id is not None and str(company_id) not in companies:
        raise HTTPException(status.HTTP_404_NOT_FOUND, COMPANY_NOT_FOUND)


def foreign_company(arguments: dict, companies: frozenset[str]) -> bool:
    """Whether a tool's arguments name a company that isn't one of the user's."""
    company_id = arguments.get("company_id")

    return company_id is not None and str(company_id) not in companies
