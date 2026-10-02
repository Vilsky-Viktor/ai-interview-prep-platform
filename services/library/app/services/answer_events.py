import asyncio
import json
import logging
import socket
import time
import uuid

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.config.settings import settings
from app.constants.events import (
    ANSWER_RECORDED,
    CONSUMER_GROUP,
    EVENTS_STREAM,
    READ_BLOCK_MS,
    READ_COUNT,
    READ_SOCKET_TIMEOUT_S,
    RECLAIM_IDLE_MS,
    RECLAIM_INTERVAL_S,
    RESTART_DELAY_S,
)
from app.services.quality import review
from app.storage import quality

logger = logging.getLogger(__name__)


async def handle(event_type: str, data: dict) -> None:
    """Adds one answer to its question's statistics; other events aren't ours."""
    if event_type == ANSWER_RECORDED:
        question_id = uuid.UUID(data["question_id"])
        await quality.record_answer(
            question_id, data["question_text"], data["option"], data["correct"]
        )
        await review(question_id)


async def process(redis: Redis, entry_id: str, fields: dict) -> None:
    """Acknowledges only once handled, so a failure is retried by the next reclaim."""
    try:
        await handle(fields["type"], json.loads(fields["data"]))
    except Exception:
        logger.exception("Failed to handle event %s", entry_id)

        return

    await redis.xack(EVENTS_STREAM, CONSUMER_GROUP, entry_id)


async def ensure_group(redis: Redis) -> None:
    try:
        await redis.xgroup_create(EVENTS_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
    except ResponseError as error:
        if "BUSYGROUP" not in str(error):
            raise


async def reclaim(redis: Redis, consumer: str) -> None:
    _, reclaimed, _ = await redis.xautoclaim(
        EVENTS_STREAM, CONSUMER_GROUP, consumer, min_idle_time=RECLAIM_IDLE_MS
    )

    for entry_id, fields in reclaimed:
        await process(redis, entry_id, fields)


async def consume() -> None:
    """Runs for the life of the app, next to the API (see main.py), and survives Redis outages."""
    while True:
        try:
            await listen()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Event listener stopped; starting again")
            await asyncio.sleep(RESTART_DELAY_S)


async def listen() -> None:
    redis = Redis.from_url(
        settings.redis_url, decode_responses=True, socket_timeout=READ_SOCKET_TIMEOUT_S
    )
    consumer = socket.gethostname()
    await ensure_group(redis)
    next_reclaim = 0.0

    try:
        while True:
            if time.monotonic() >= next_reclaim:
                await reclaim(redis, consumer)
                next_reclaim = time.monotonic() + RECLAIM_INTERVAL_S

            response = await redis.xreadgroup(
                CONSUMER_GROUP,
                consumer,
                {EVENTS_STREAM: ">"},
                count=READ_COUNT,
                block=READ_BLOCK_MS,
            )

            for _, entries in response:
                for entry_id, fields in entries:
                    await process(redis, entry_id, fields)
    finally:
        await redis.aclose()
