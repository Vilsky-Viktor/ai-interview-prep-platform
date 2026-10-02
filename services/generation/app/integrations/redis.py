from functools import cache

from redis.asyncio import Redis

from app.config.settings import settings


@cache
def get_redis() -> Redis:
    """For rate limits, the shared LLM limiter and the draft cache; events go through Pub/Sub."""
    return Redis.from_url(settings.redis_url)
