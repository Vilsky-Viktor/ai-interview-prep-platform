import hashlib
import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.constants.api import IDEMPOTENCY_IN_PROGRESS, IDEMPOTENCY_SECONDS
from app.integrations.redis import get_redis

logger = logging.getLogger(__name__)
PENDING = "pending"


async def once(company_id: UUID, key: str | None, run: Callable[[], Awaitable[str]]) -> str:
    """Runs `run` once per `Idempotency-Key` of the company within IDEMPOTENCY_SECONDS: a retry
    with the same key gets the first run's result (an id) without running it again, and one
    while the first still runs is refused (409). A run that fails frees the key. Without a key,
    or with Redis down, it just runs."""
    if not key:
        return await run()

    redis = get_redis()
    digest = hashlib.sha256(key.encode()).hexdigest()
    name = f"api:idempotency:{company_id}:{digest}"

    try:
        claimed = await redis.set(name, PENDING, nx=True, ex=IDEMPOTENCY_SECONDS)
        stored = None if claimed else await redis.get(name)
        earlier = stored.decode() if stored is not None else None
    except RedisError as error:
        logger.warning("Idempotency-Key skipped, Redis failed: %s", error)

        return await run()

    if earlier == PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, IDEMPOTENCY_IN_PROGRESS)

    if earlier is not None:
        return earlier

    try:
        result = await run()
    except Exception:
        await redis.delete(name)

        raise

    await redis.set(name, result, ex=IDEMPOTENCY_SECONDS)

    return result
