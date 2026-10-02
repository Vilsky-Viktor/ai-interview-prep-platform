from functools import cache

from redis.asyncio import Redis

from app.config.settings import settings


@cache
def get_redis() -> Redis:
    """For rate limits; events go through Pub/Sub (prepza_common.pubsub)."""
    return Redis.from_url(settings.redis_url)
