from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import app.models.audit
import app.models.companies
import app.models.events
import app.models.interviews
import app.models.invites
import app.models.outbox  # noqa: F401
from app.config.settings import settings
from app.models.base import Base

fileConfig(context.config.config_file_name)

engine = create_engine(settings.sqlalchemy_url)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)

    with context.begin_transaction():
        context.run_migrations()
