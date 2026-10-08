"""Integration tests run against a real, freshly migrated database and a real Redis. They run
only with INTEGRATION_TESTS set (see scripts/integration.sh); plain `pytest` skips them."""

import asyncio
import os
import uuid

import firebase_admin
import httpx
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


@pytest.fixture
def user():
    """A new Auth emulator user: (uid, ID token); the user is deleted after the test. The
    assistant checks the token as it does in the running stack."""
    if not firebase_admin._apps:
        firebase_admin.initialize_app(options={"projectId": os.environ["FIREBASE_PROJECT_ID"]})

    auth = f"http://{os.environ['FIREBASE_AUTH_EMULATOR_HOST']}/identitytoolkit.googleapis.com/v1"
    email = f"assistant-{uuid.uuid4().hex[:8]}@example.com"
    found = httpx.post(
        f"{auth}/accounts:signUp?key=demo",
        json={"email": email, "password": "secret123", "returnSecureToken": True},
    ).json()

    yield found["localId"], found["idToken"]

    httpx.post(
        f"{auth}/projects/{os.environ['FIREBASE_PROJECT_ID']}/accounts:delete",
        json={"localId": found["localId"]},
        headers={"Authorization": "Bearer owner"},
    )


@pytest.fixture
def token(user):
    return user[1]


@pytest.fixture(autouse=True)
def no_openai_titles(monkeypatch):
    """Titles come from a fake model: integration tests never call OpenAI."""
    from app.integrations import llm
    from tests.fake_model import FakeTitleModel

    monkeypatch.setattr(llm, "get_title_model", lambda: FakeTitleModel("Your companies"))
