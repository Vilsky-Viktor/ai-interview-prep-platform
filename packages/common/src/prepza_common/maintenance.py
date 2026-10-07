# Maintenance mode (internal_docs/compliance/post-market-monitoring-plan.md, section 4): a superadmin turns
# it on, and every service's API refuses every request with a 503, except superadmins and the
# paths in MAINTENANCE_OPEN_PATHS and MAINTENANCE_OPEN_PREFIXES. Like the emergency pause, it's
# one Redis key without expiry.
import logging

from fastapi import HTTPException, status
from prepza_common.auth import verify
from prepza_common.constants import (
    MAINTENANCE,
    MAINTENANCE_KEY,
    MAINTENANCE_OPEN_PATHS,
    MAINTENANCE_OPEN_PREFIXES,
)
from prepza_common.i18n import request_language, translate
from prepza_common.superadmin import is_superadmin
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def is_on(redis) -> bool:
    """With Redis down, off: the switch must never stop the service by itself."""
    try:
        return bool(await redis.exists(MAINTENANCE_KEY))
    except Exception:
        logger.warning("Couldn't read the maintenance switch; treating it as off", exc_info=True)

        return False


async def set_on(redis, on: bool, user_id: str) -> None:
    """Who switched it and when is kept in the logs."""
    if on:
        await redis.set(MAINTENANCE_KEY, user_id)
    else:
        await redis.delete(MAINTENANCE_KEY)

    logger.warning("Maintenance mode turned %s by superadmin %s", "on" if on else "off", user_id)


def is_open(path: str) -> bool:
    return path in MAINTENANCE_OPEN_PATHS or path.startswith(MAINTENANCE_OPEN_PREFIXES)


async def is_superadmin_request(request: Request) -> bool:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")

    if scheme.lower() != "bearer" or not token:
        return False

    # Checking the token may fetch Google's certificates: off the event loop, as FastAPI does.
    try:
        user = await run_in_threadpool(verify, token)
    except HTTPException:
        return False

    return user is not None and is_superadmin(user)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """Added in each service's main.py with the service's own Redis client."""

    def __init__(self, app, get_redis):
        super().__init__(app)
        self.get_redis = get_redis

    async def dispatch(self, request: Request, call_next):
        if is_open(request.url.path) or not await is_on(self.get_redis()):
            return await call_next(request)

        if await is_superadmin_request(request):
            return await call_next(request)

        message = translate(MAINTENANCE, request_language(request))

        return JSONResponse({"detail": message}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
