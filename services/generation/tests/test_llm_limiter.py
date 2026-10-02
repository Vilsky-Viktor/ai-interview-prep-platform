import asyncio

from app.integrations import llm_limiter
from app.integrations.llm_limiter import SharedRateLimiter


class FakePipeline:
    def __init__(self, counts):
        self.counts = counts
        self.key = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def incr(self, key):
        self.key = key

    def expire(self, key, seconds):
        pass

    async def execute(self):
        self.counts[self.key] = self.counts.get(self.key, 0) + 1

        return self.counts[self.key], True


class FakeRedis:
    def __init__(self, down=False):
        self.counts = {}
        self.down = down

    def pipeline(self, transaction):
        if self.down:
            raise ConnectionError("Redis is down")

        return FakePipeline(self.counts)


def test_requests_over_the_limit_wait_for_the_next_second(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(llm_limiter, "get_redis", lambda: redis)
    monkeypatch.setattr(llm_limiter.time, "time", lambda: 1000.5)
    limiter = SharedRateLimiter(per_second=2)

    async def three():
        return [await limiter.aacquire(blocking=False) for _ in range(3)]

    assert asyncio.run(three()) == [True, True, False]


def test_without_redis_requests_are_not_held_back(monkeypatch):
    monkeypatch.setattr(llm_limiter, "get_redis", lambda: FakeRedis(down=True))

    assert asyncio.run(SharedRateLimiter(per_second=1).aacquire()) is True
