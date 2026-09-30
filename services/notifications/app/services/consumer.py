import json
import logging
import socket
import time

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.config.settings import settings
from app.constants.events import (
    ATTEMPTS_KEY,
    CANDIDATE_INVITED,
    CONSUMER_GROUP,
    DEAD_LETTER_MAX_LENGTH,
    DEAD_LETTER_STREAM,
    EVENTS_STREAM,
    MAX_ATTEMPTS,
    PREPARATION_SHARED,
    READ_BLOCK_MS,
    READ_COUNT,
    READ_SOCKET_TIMEOUT_S,
    RECLAIM_IDLE_MS,
    RECLAIM_INTERVAL_S,
)
from app.helpers.emails import candidate_invite_email, share_invite_email
from app.integrations import smtp

logger = logging.getLogger(__name__)


async def handle(event_type: str, data: dict) -> None:
    if event_type == PREPARATION_SHARED:
        await smtp.send(share_invite_email(data, settings.site_url, settings.mail_from))

    if event_type == CANDIDATE_INVITED:
        await smtp.send(candidate_invite_email(data, settings.site_url, settings.mail_from))


async def process(redis: Redis, entry_id: str, fields: dict) -> None:
    """Acknowledges only after the email went out, so a failure is retried later.

    After MAX_ATTEMPTS failures the event moves to the dead-letter stream instead, so one
    broken event can't be retried forever.
    """
    try:
        await handle(fields["type"], json.loads(fields["data"]))
    except Exception as error:
        attempts = await redis.hincrby(ATTEMPTS_KEY, entry_id, 1)

        if attempts < MAX_ATTEMPTS:
            logger.exception("Failed to handle event %s (attempt %d)", entry_id, attempts)

            return

        logger.exception("Giving up on event %s after %d attempts", entry_id, attempts)
        await redis.xadd(
            DEAD_LETTER_STREAM,
            {**fields, "entry_id": entry_id, "error": repr(error)},
            maxlen=DEAD_LETTER_MAX_LENGTH,
            approximate=True,
        )

    await redis.xack(EVENTS_STREAM, CONSUMER_GROUP, entry_id)
    await redis.hdel(ATTEMPTS_KEY, entry_id)


async def ensure_group(redis: Redis) -> None:
    try:
        await redis.xgroup_create(EVENTS_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
    except ResponseError as error:
        if "BUSYGROUP" not in str(error):
            raise


async def reclaim(redis: Redis, consumer: str) -> None:
    """Retries events left pending by a failure or a crashed consumer."""
    _, reclaimed, _ = await redis.xautoclaim(
        EVENTS_STREAM, CONSUMER_GROUP, consumer, min_idle_time=RECLAIM_IDLE_MS
    )

    for entry_id, fields in reclaimed:
        await process(redis, entry_id, fields)


async def consume() -> None:
    redis = Redis.from_url(
        settings.redis_url, decode_responses=True, socket_timeout=READ_SOCKET_TIMEOUT_S
    )
    consumer = socket.gethostname()
    await ensure_group(redis)
    logger.info("Consuming %s as %s", EVENTS_STREAM, consumer)
    next_reclaim = 0.0

    while True:
        if time.monotonic() >= next_reclaim:
            await reclaim(redis, consumer)
            next_reclaim = time.monotonic() + RECLAIM_INTERVAL_S

        response = await redis.xreadgroup(
            CONSUMER_GROUP, consumer, {EVENTS_STREAM: ">"}, count=READ_COUNT, block=READ_BLOCK_MS
        )

        for _, entries in response:
            for entry_id, fields in entries:
                await process(redis, entry_id, fields)
