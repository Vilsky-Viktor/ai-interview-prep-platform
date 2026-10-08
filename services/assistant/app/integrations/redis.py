from functools import cache

from redis.asyncio import Redis

from app.config.settings import settings


@cache
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)
