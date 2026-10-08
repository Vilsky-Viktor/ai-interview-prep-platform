from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prepza_common.rate_limit import hit

from app.constants.api import MINUTE_SECONDS, REQUESTS_PER_MINUTE
from app.helpers.keys import expired, hashed
from app.integrations import companies
from app.integrations.redis import get_redis
from app.models.api import ApiKey
from app.storage import keys

bearer = HTTPBearer(auto_error=False, description="A company's API key: `Bearer pz_...`")


async def api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> ApiKey:
    """The API key the request carries. It works until it expires, while whoever made it is still
    an owner or admin of its company, up to REQUESTS_PER_MINUTE requests a minute."""
    found = await keys.by_hash(hashed(credentials.credentials)) if credentials else None

    if found is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")

    if expired(found.expires_at, datetime.now(UTC)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "This API key has expired")

    await hit(get_redis(), f"rate:api:{found.id}", REQUESTS_PER_MINUTE, MINUTE_SECONDS)
    access = await companies.access(found.company_id, found.created_by)

    if not access["editor"]:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "This key's creator is no longer an owner or admin of the company",
        )

    await keys.used(found.id)

    return found


ApiKeyDep = Annotated[ApiKey, Depends(api_key)]
