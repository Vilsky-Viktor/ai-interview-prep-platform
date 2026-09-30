from fastapi import HTTPException, status

RATE_LIMITED = "Too many requests. Try again later."


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
