"""Integration tests run against a real, freshly migrated database and a real Redis. They run
only with INTEGRATION_TESTS set (see scripts/integration.sh); plain `pytest` skips them."""

import asyncio
import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

if not os.getenv("INTEGRATION_TESTS"):
    collect_ignore_glob = ["test_*.py"]


@pytest.fixture(scope="session", autouse=True)
def database():
    """Creates the test database from scratch, runs every migration, and drops it afterwards."""
    url = make_url(os.environ["DATABASE_URL"])
    admin = create_engine(
        url.set(drivername="postgresql+psycopg", database="postgres"),
        isolation_level="AUTOCOMMIT",
    )

    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{url.database}"'))

    command.upgrade(Config("alembic.ini"), "head")

    yield

    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))

    admin.dispose()


@pytest.fixture
def run():
    """Runs a coroutine on a fresh event loop; the database pool and the Redis and HTTP clients
    are closed after, as their connections belong to that loop."""
    from prepza_common import http

    from app.integrations.redis import get_redis
    from app.storage.db import engine

    def run(coroutine):
        async def wrapped():
            try:
                return await coroutine
            finally:
                await engine.dispose()
                await get_redis().aclose()
                get_redis.cache_clear()
                await http.get_client().aclose()
                http.get_client.cache_clear()

        return asyncio.run(wrapped())

    return run
