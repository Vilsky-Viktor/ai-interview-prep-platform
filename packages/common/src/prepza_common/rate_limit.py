from fastapi import HTTPException, status
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS, RATE_LIMITED


async def hit(redis, key: str, limit: int, window: int) -> None:
    if limit <= 0:
        return

    # One transaction, so the counter never exists without its expiry.
    async with redis.pipeline(transaction=True) as pipe:
        pipe.set(key, 0, ex=window, nx=True)
        pipe.incr(key)
        _, count = await pipe.execute()

    if count > limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, RATE_LIMITED)


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
