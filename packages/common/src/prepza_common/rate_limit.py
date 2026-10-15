import logging

from fastapi import HTTPException, status
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS, RATE_LIMITED

logger = logging.getLogger(__name__)


async def hit(redis, key: str, limit: int, window: int, message: str = RATE_LIMITED) -> None:
    """Counts one use in the window; over `limit`, a 429 with `message`. With Redis down, an
    error: the request fails rather than going unlimited (see hit_or_skip)."""
    if limit <= 0:
        return

    # One transaction, so the counter never exists without its expiry.
    async with redis.pipeline(transaction=True) as pipe:
        pipe.set(key, 0, ex=window, nx=True)
        pipe.incr(key)
        _, count = await pipe.execute()

    if count > limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, message)


async def spend(
    redis, key: str, amount: int, limit: int, window: int, message: str = RATE_LIMITED
) -> None:
    """Adds `amount` (a cost, such as tokens or micro-dollars) to the window's total; once the
    total is over `limit`, a 429 with `message`. An `amount` of 0 only checks the budget. With
    Redis down, an error, as with hit."""
    if limit <= 0:
        return

    # One transaction, so the total never exists without its expiry.
    async with redis.pipeline(transaction=True) as pipe:
        pipe.set(key, 0, ex=window, nx=True)
        pipe.incrby(key, amount)
        _, total = await pipe.execute()

    if total > limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, message)


async def hit_or_skip(
    redis, key: str, limit: int, window: int, message: str = RATE_LIMITED
) -> None:
    """hit(), except that with Redis down the use goes uncounted rather than refused: for limits
    against abuse, where refusing everyone while Redis is down would be worse."""
    try:
        await hit(redis, key, limit, window, message)
    except HTTPException:
        raise
    except Exception:
        logger.warning("The %s limit skipped, Redis failed", key.rsplit(":", 1)[0], exc_info=True)


async def add_spent(redis, key: str, amount: int, limit: int, window: int) -> None:
    """Adds what a finished request cost to its budget. Going over refuses the next request,
    not this one; with Redis down, the cost is lost rather than the request's result."""
    try:
        await spend(redis, key, amount, limit, window)
    except HTTPException:
        pass
    except Exception:
        logger.warning(
            "Spending on %s not counted, Redis failed", key.rsplit(":", 1)[0], exc_info=True
        )


async def hit_emails(
    redis, sender: str, recipient: str, per_hour: int, per_day: int, per_recipient: int
) -> None:
    """Limits invite emails, so nobody can spam from our domain.

    The sender's counts are shared by every service that sends invites. `recipient` names the
    address and what it's invited to, so resending to one person is limited on its own.
    """
    await hit(redis, f"rate:emails:hour:{sender}", per_hour, HOUR_SECONDS)
    await hit(redis, f"rate:emails:day:{sender}", per_day, DAY_SECONDS)
    await hit(redis, f"rate:emails:recipient:{recipient}", per_recipient, DAY_SECONDS)
