import uuid

import pytest
from fastapi import HTTPException
from prepza_common.rate_limit import hit_emails
from redis.asyncio import Redis

from app.config.settings import settings


def test_email_limits_count_in_real_redis(run):
    sender = f"sender-{uuid.uuid4()}"

    async def scenario():
        redis = Redis.from_url(settings.redis_url)

        try:
            for _ in range(3):
                await hit_emails(redis, sender, "interview:carol@example.com", 30, 200, 3)

            with pytest.raises(HTTPException) as refused:
                await hit_emails(redis, sender, "interview:carol@example.com", 30, 200, 3)

            ttl = await redis.ttl("rate:emails:recipient:interview:carol@example.com")
            await redis.delete(
                f"rate:emails:hour:{sender}",
                f"rate:emails:day:{sender}",
                "rate:emails:recipient:interview:carol@example.com",
            )
        finally:
            await redis.aclose()

        return refused.value.status_code, ttl

    status, ttl = run(scenario())

    assert status == 429
    # Every counter expires, so a limit never sticks forever.
    assert 0 < ttl <= 24 * 60 * 60
