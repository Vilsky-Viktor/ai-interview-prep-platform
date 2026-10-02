from prepza_common.db import database
from prepza_common.db import ping as ping_engine

from app.config.settings import settings

engine, Session = database(settings.sqlalchemy_url)


async def ping() -> None:
    """Raises if the database doesn't answer."""
    await ping_engine(engine)
