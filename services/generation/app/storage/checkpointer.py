from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config.settings import settings


async def open_checkpointer() -> tuple[AsyncConnectionPool, AsyncPostgresSaver]:
    pool = AsyncConnectionPool(
        settings.database_url,
        open=False,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
    )
    await pool.open()
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()

    return pool, checkpointer
