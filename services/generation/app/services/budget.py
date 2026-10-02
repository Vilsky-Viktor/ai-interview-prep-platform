from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.generation import BUDGET_KEY, BUDGET_KEY_SECONDS, GENERATIONS_PAUSED
from app.integrations.redis import get_redis


async def use_daily_budget() -> None:
    """Counts one new generation against today's limit for everyone (UTC days); past it, new
    generations wait until tomorrow. Checked before billing, so nobody pays for a refusal."""
    if settings.daily_generation_limit <= 0:
        return

    key = f"{BUDGET_KEY}:{datetime.now(UTC).date().isoformat()}"

    async with get_redis().pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, BUDGET_KEY_SECONDS)
        count, _ = await pipe.execute()

    if count > settings.daily_generation_limit:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, GENERATIONS_PAUSED)
