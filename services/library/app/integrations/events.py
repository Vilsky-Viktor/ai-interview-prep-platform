import json
from functools import cache

from redis.asyncio import Redis

from app.config.settings import settings
from app.constants.events import EVENTS_MAX_LENGTH, EVENTS_STREAM


@cache
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)


async def publish(event_type: str, data: dict) -> None:
    """Appends a domain event to the stream that `notifications` consumes."""
    await get_redis().xadd(
        EVENTS_STREAM,
        {"type": event_type, "data": json.dumps(data)},
        maxlen=EVENTS_MAX_LENGTH,
        approximate=True,
    )
