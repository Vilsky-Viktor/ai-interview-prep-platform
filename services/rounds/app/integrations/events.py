import json

from app.constants.events import EVENTS_MAX_LENGTH, EVENTS_STREAM
from app.integrations.redis import get_redis


async def publish(event_type: str, data: dict) -> None:
    """Appends a domain event to the stream other services consume."""
    await get_redis().xadd(
        EVENTS_STREAM,
        {"type": event_type, "data": json.dumps(data)},
        maxlen=EVENTS_MAX_LENGTH,
        approximate=True,
    )
