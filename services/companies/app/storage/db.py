from prepza_common.db import database

from app.config.settings import settings

engine, Session = database(settings.database_url)
