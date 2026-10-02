from prepza_common.constants import DB_MAX_OVERFLOW, DB_POOL_SIZE
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


def database(url: str) -> tuple[AsyncEngine, async_sessionmaker]:
    """The engine and session factory for a service's database."""
    engine = create_async_engine(
        url, pool_pre_ping=True, pool_size=DB_POOL_SIZE, max_overflow=DB_MAX_OVERFLOW
    )

    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def ping(engine: AsyncEngine) -> None:
    """Raises if the database doesn't answer."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
