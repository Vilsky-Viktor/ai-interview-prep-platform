import uuid

from redis.asyncio import Redis

from app.config.settings import settings
from app.storage import draft_cache


def test_a_cached_draft_reads_back_and_expires(run, monkeypatch):
    source = f"prompt {uuid.uuid4()}"

    async def scenario():
        redis = Redis.from_url(settings.redis_url)
        monkeypatch.setattr(draft_cache, "get_redis", lambda: redis)

        try:
            missing = await draft_cache.get("topics", source)
            await draft_cache.put("topics", source, [{"main_topic": "Python"}])
            found = await draft_cache.get("topics", source)
            ttl = await redis.ttl(draft_cache.cache_key("topics", source))
            await redis.delete(draft_cache.cache_key("topics", source))
        finally:
            await redis.aclose()

        return missing, found, ttl

    missing, found, ttl = run(scenario())

    assert missing is None
    assert found == [{"main_topic": "Python"}]
    assert ttl > 0
