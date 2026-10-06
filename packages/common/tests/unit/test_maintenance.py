import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prepza_common import maintenance
from prepza_common.constants import MAINTENANCE, MAINTENANCE_KEY
from prepza_common.maintenance import MaintenanceMiddleware, is_on, set_on
from prepza_common.translations import TRANSLATIONS
from prepza_common.user import User


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def exists(self, key):
        return int(key in self.values)

    async def set(self, key, value):
        self.values[key] = value

    async def delete(self, key):
        self.values.pop(key, None)


class DownRedis:
    async def exists(self, key):
        raise ConnectionError("Redis is down")


REDIS = FakeRedis()
app = FastAPI()
app.add_middleware(MaintenanceMiddleware, get_redis=lambda: REDIS)

PATHS = [
    "/companies",
    "/sessions/1/answers",
    "/health",
    "/ready",
    "/maintenance",
    "/superadmin/maintenance",
    "/internal/events",
    "/internal/schedules/outbox",
    "/webhooks/paddle",
    "/webhooks/resend",
]
OPEN = PATHS[2:]

for path in PATHS:
    app.add_api_route(path, lambda: {"ok": True}, methods=["GET", "POST"])

client = TestClient(app)


@pytest.fixture(autouse=True)
def switched_on(monkeypatch):
    """On, with ann as the only superadmin; a token is the email it signs in."""
    REDIS.values = {MAINTENANCE_KEY: "ann"}
    monkeypatch.setenv("SUPERADMIN_EMAILS", "ann@example.com")
    monkeypatch.setattr(
        maintenance,
        "verify",
        lambda token: User(uid=token, email=token, email_verified=True),
    )


def test_every_other_request_gets_a_translated_503():
    for path in PATHS[:2]:
        refused = client.post(path, headers={"Accept-Language": "uk"})

        assert refused.status_code == 503
        assert refused.json()["detail"] == TRANSLATIONS["uk"][MAINTENANCE]

    assert client.get("/companies").json()["detail"] == MAINTENANCE


def test_health_the_switch_internal_calls_and_webhooks_stay_open():
    for path in OPEN:
        assert client.post(path).status_code == 200


def test_a_superadmin_passes_and_others_signed_in_do_not():
    superadmin = {"Authorization": "Bearer ann@example.com"}

    assert client.get("/companies", headers=superadmin).status_code == 200

    other = {"Authorization": "Bearer bob@example.com"}

    assert client.get("/companies", headers=other).status_code == 503


def test_an_invalid_token_is_refused(monkeypatch):
    monkeypatch.setattr(maintenance, "verify", lambda token: None)

    assert client.get("/companies", headers={"Authorization": "Bearer x"}).status_code == 503


def test_off_everything_passes():
    REDIS.values = {}

    assert client.get("/companies").status_code == 200


def test_with_redis_down_it_is_off(monkeypatch):
    assert not asyncio.run(is_on(DownRedis()))

    monkeypatch.setitem(globals(), "REDIS", DownRedis())

    assert client.get("/companies").status_code == 200


def test_the_switch_turns_on_and_off_and_remembers_who():
    redis = FakeRedis()

    asyncio.run(set_on(redis, True, "ann"))

    assert redis.values == {MAINTENANCE_KEY: "ann"}
    assert asyncio.run(is_on(redis))

    asyncio.run(set_on(redis, False, "ann"))

    assert not asyncio.run(is_on(redis))


def test_the_message_has_translations():
    for language in TRANSLATIONS.values():
        assert MAINTENANCE in language
