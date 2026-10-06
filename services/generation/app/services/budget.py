from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.generation import BUDGET_KEY, BUDGET_KEY_SECONDS, GENERATIONS_PAUSED
from app.constants.quality import DAILY_VERIFY_LIMIT, VERIFY_BUDGET_KEY, VERIFY_PAUSED
from app.integrations.redis import get_redis


async def count_today(key: str) -> int:
    """Counts one use under `key` for today (UTC days); today's count so far."""
    day_key = f"{key}:{datetime.now(UTC).date().isoformat()}"

    async with get_redis().pipeline(transaction=True) as pipe:
        pipe.incr(day_key)
        pipe.expire(day_key, BUDGET_KEY_SECONDS)
        count, _ = await pipe.execute()

    return count


async def use_daily_budget() -> None:
    """Counts one new generation against today's limit for everyone (UTC days); past it, new
    generations wait until tomorrow. Checked before billing, so nobody pays for a refusal."""
    if settings.daily_generation_limit <= 0:
        return

    if await count_today(BUDGET_KEY) > settings.daily_generation_limit:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, GENERATIONS_PAUSED)


async def use_verify_budget() -> None:
    """Counts one verifier job against today's limit for everyone: reports and answers can't
    drive unlimited rewrites. Past it, the library keeps the flag and sends it again later."""
    if await count_today(VERIFY_BUDGET_KEY) > DAILY_VERIFY_LIMIT:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, VERIFY_PAUSED)
