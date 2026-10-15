import logging

from fastapi import HTTPException
from mcp.server.auth.provider import TokenError
from prepza_common.client_ip import client_ip
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS, MINUTE_SECONDS
from prepza_common.rate_limit import hit
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.constants.limits import TOKEN_REQUESTS_PER_CLIENT_MINUTE
from app.integrations.redis import get_redis

logger = logging.getLogger(__name__)


class Limited:
    """An endpoint of the OAuth server counted per address in an hour, and with `daily`, for
    everyone in a day; over a limit, refused (429) with an OAuth `error`. With Redis down, not
    counted rather than refused."""

    def __init__(
        self, app: ASGIApp, name: str, error: str, per_ip_hour: int, daily: int | None = None
    ):
        self.app = app
        self.name = name
        self.error = error
        self.per_ip_hour = per_ip_hour
        self.daily = daily

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] in ("GET", "POST"):
            redis = get_redis()
            key = f"rate:assistant:mcp:{self.name}"

            try:
                address = client_ip(Request(scope))
                await hit(redis, f"{key}:{address}", self.per_ip_hour, HOUR_SECONDS)

                if self.daily is not None:
                    await hit(redis, key, self.daily, DAY_SECONDS)
            except HTTPException as error:
                body = {"error": self.error, "error_description": error.detail}
                await JSONResponse(body, status_code=error.status_code)(scope, receive, send)

                return
            except Exception:
                logger.warning("The %s limit skipped, Redis failed", self.name, exc_info=True)

        await self.app(scope, receive, send)


async def limit_tokens(client_id: str) -> None:
    """Counts one token request of the app; over the limit, refused. With Redis down, not
    counted rather than refused."""
    key = f"rate:assistant:mcp:token:{client_id}"

    try:
        await hit(get_redis(), key, TOKEN_REQUESTS_PER_CLIENT_MINUTE, MINUTE_SECONDS)
    except HTTPException:
        raise TokenError("invalid_request", "Too many token requests; try again in a minute.")
    except Exception:
        logger.warning("Token request limit skipped, Redis failed", exc_info=True)
