import asyncio
import logging
import time

from langchain_core.rate_limiters import BaseRateLimiter

from app.constants.generation import LLM_RATE_KEY
from app.integrations.events import get_redis

logger = logging.getLogger(__name__)


class SharedRateLimiter(BaseRateLimiter):
    """At most `per_second` LLM requests a second across every generation process.

    Counted in Redis per second, so the API and all workers share one budget. Chat (rounds)
    isn't limited here, which keeps it ahead of bulk generation.
    """

    def __init__(self, per_second: int):
        self.per_second = per_second

    def acquire(self, *, blocking: bool = True) -> bool:
        # Every call here is async; a sync call isn't held back.
        return True

    async def aacquire(self, *, blocking: bool = True) -> bool:
        while True:
            second = int(time.time())

            try:
                async with get_redis().pipeline(transaction=True) as pipe:
                    pipe.incr(f"{LLM_RATE_KEY}:{second}")
                    pipe.expire(f"{LLM_RATE_KEY}:{second}", 2)
                    count, _ = await pipe.execute()
            except Exception:
                # Without Redis, generation goes on unlimited rather than stopping.
                logger.exception("Couldn't check the LLM rate limit")

                return True

            if count <= self.per_second:
                return True

            if not blocking:
                return False

            await asyncio.sleep(max(0.0, second + 1 - time.time()))
