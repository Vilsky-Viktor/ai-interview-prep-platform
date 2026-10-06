"""Integration tests run against a real, freshly migrated database. They run only with
INTEGRATION_TESTS set (see scripts/tests/integration.sh); plain `pytest` skips them."""

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
    """Runs a coroutine on a fresh event loop; the pool is emptied after, as its connections
    belong to that loop."""
    from app.storage.db import engine

    def run(coroutine):
        async def wrapped():
            try:
                return await coroutine
            finally:
                await engine.dispose()

        return asyncio.run(wrapped())

    return run


@pytest.fixture
def paddle_calls(monkeypatch):
    """Paddle's API, faked: what was charged and cancelled. A subscription whose id starts
    with sub_ended has ended in Paddle; one starting with sub_declined has a declined card."""
    from app.config.settings import settings
    from app.integrations import paddle

    calls = []

    async def charge(subscription_id, price_id):
        calls.append(("charge", subscription_id, price_id))

        if subscription_id.startswith("sub_declined"):
            raise RuntimeError("declined")

    async def cancel(subscription_id):
        calls.append(("cancel", subscription_id))

    async def subscription_status(subscription_id):
        return "canceled" if subscription_id.startswith("sub_ended") else "active"

    monkeypatch.setattr(paddle, "charge", charge)
    monkeypatch.setattr(paddle, "cancel", cancel)
    monkeypatch.setattr(paddle, "subscription_status", subscription_status)
    monkeypatch.setattr(settings, "paddle_api_key", "key")
    monkeypatch.setattr(settings, "paddle_price_auto_top_up", "pri_plan")
    monkeypatch.setattr(settings, "paddle_price_topup_30", "pri_30")

    return calls
