class FakePipeline:
    """The SET NX + INCR transaction of prepza_common.rate_limit.hit, in memory."""

    def __init__(self, redis):
        self.redis = redis
        self.keys = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def set(self, key, value, ex, nx):
        self.redis.counts.setdefault(key, value)

    def incr(self, key):
        self.keys.append(key)

    async def execute(self):
        key = self.keys.pop()
        self.redis.counts[key] += 1

        return [True, self.redis.counts[key]]


class FakeRedis:
    def __init__(self):
        self.counts = {}

    def pipeline(self, transaction):
        return FakePipeline(self)
