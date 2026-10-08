import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prepza_common import memory_cache
from prepza_common.rate_limit import hit
from redis.exceptions import RedisError

from app.constants.api import (
    ACCESS_CACHE_SECONDS,
    LAST_USED_EVERY,
    MINUTE_SECONDS,
    REQUESTS_PER_MINUTE,
)
from app.helpers.keys import expired, hashed
from app.integrations import companies
from app.integrations.redis import get_redis
from app.models.api import ApiKey
from app.storage import keys

logger = logging.getLogger(__name__)

bearer = HTTPBearer(auto_error=False, description="A company's API key: `Bearer pz_...`")


async def api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> ApiKey:
    """The API key the request carries. It works until it expires, while whoever made it is still
    an owner or admin of its company, up to REQUESTS_PER_MINUTE requests a minute for the whole
    company."""
    found = await keys.by_hash(hashed(credentials.credentials)) if credentials else None

    if found is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")

    now = datetime.now(UTC)

    if expired(found.expires_at, now):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "This API key has expired")

    await limit(found.company_id)

    if not await editor(found.company_id, found.created_by):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "This key's creator is no longer an owner or admin of the company",
        )

    if found.last_used_at is None or now - found.last_used_at >= LAST_USED_EVERY:
        await keys.used(found.id)

    return found


async def limit(company_id: UUID) -> None:
    """Counts the request against its company. With Redis down, requests go through
    unlimited rather than all failing."""
    try:
        await hit(get_redis(), f"rate:api:{company_id}", REQUESTS_PER_MINUTE, MINUTE_SECONDS)
    except RedisError as error:
        logger.warning("API rate limit skipped, Redis failed: %s", error)


async def editor(company_id: UUID, user_id: str) -> bool:
    """Whether the key's maker is still an owner or admin, as companies said within
    ACCESS_CACHE_SECONDS."""
    key = f"api:editor:{company_id}:{user_id}"
    found = memory_cache.get(key)

    if found is None:
        found = (await companies.access(company_id, user_id))["editor"]
        memory_cache.put(key, found, ACCESS_CACHE_SECONDS)

    return found


ApiKeyDep = Annotated[ApiKey, Depends(api_key)]
