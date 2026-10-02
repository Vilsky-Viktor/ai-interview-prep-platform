import asyncio

from app.helpers.logging import configure_logging
from app.integrations.sentry import init_sentry
from app.services.consumer import consume

if __name__ == "__main__":
    configure_logging()
    init_sentry()
    asyncio.run(consume())
