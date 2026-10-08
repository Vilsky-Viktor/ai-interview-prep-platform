from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import app.models.api  # noqa: F401
from app.config.settings import settings
from app.models.base import Base

fileConfig(context.config.config_file_name)

engine = create_engine(settings.sqlalchemy_url)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)

    with context.begin_transaction():
        context.run_migrations()
