import asyncio

from app.helpers.logging import configure_logging
from app.services.consumer import consume

if __name__ == "__main__":
    configure_logging()
    asyncio.run(consume())
