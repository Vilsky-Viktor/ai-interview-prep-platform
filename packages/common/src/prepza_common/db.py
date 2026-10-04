from prepza_common.constants import DB_MAX_OVERFLOW, DB_POOL_SIZE
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


def database(
    url: str, pool_size: int = DB_POOL_SIZE, max_overflow: int = DB_MAX_OVERFLOW
) -> tuple[AsyncEngine, async_sessionmaker]:
    """The engine and session factory for a service's database; a service with few, short queries
    takes a smaller pool, to stay within the database's connection budget."""
    engine = create_async_engine(
        url, pool_pre_ping=True, pool_size=pool_size, max_overflow=max_overflow
    )

    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def ping(engine: AsyncEngine) -> None:
    """Raises if the database doesn't answer."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
