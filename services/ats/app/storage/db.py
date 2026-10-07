from prepza_common.db import database
from prepza_common.db import ping as ping_engine

from app.config.settings import settings
from app.constants.db import DB_MAX_OVERFLOW, DB_POOL_SIZE

engine, Session = database(settings.sqlalchemy_url, DB_POOL_SIZE, DB_MAX_OVERFLOW)


async def ping() -> None:
    """Raises if the database doesn't answer."""
    await ping_engine(engine)
