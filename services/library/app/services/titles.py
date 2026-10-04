import logging

import httpx
from fastapi import HTTPException, status
from prepza_common.constants import HOUR_SECONDS
from prepza_common.rate_limit import hit

from app.constants.titles import TITLE_CHECK_FAILED, TITLE_CHECKS_PER_HOUR, TITLE_HAS_COMPANY
from app.integrations import generation
from app.integrations.redis import get_redis

logger = logging.getLogger(__name__)


async def require_no_company(title: str, user_id: str) -> None:
    """Refuses a title for a public kit when it names a company, and when it can't be
    checked, so nothing goes public unchecked."""
    await hit(get_redis(), f"rate:title-checks:{user_id}", TITLE_CHECKS_PER_HOUR, HOUR_SECONDS)

    try:
        has_company = await generation.title_has_company(title)
    except httpx.HTTPError:
        logger.exception("Couldn't check a title for company names")

        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, TITLE_CHECK_FAILED) from None

    if has_company:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, TITLE_HAS_COMPANY)
