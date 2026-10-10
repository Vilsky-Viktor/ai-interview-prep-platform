import httpx
import pytest

from app.integrations import services
from app.services import actions
from app.storage import actions as store
from tests.unit.actions_setup import COMPANY


class Writes(list):
    """The services' writes; each answers `status`."""

    status = 201


class Pipeline:
    """Runs its commands one by one on the fake."""

    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def set(self, *args, **kwargs):
        self.commands.append(self.redis.set(*args, **kwargs))

    def sadd(self, *args):
        pass

    def expire(self, *args):
        pass

    async def execute(self):
        for command in self.commands:
            await command


class FakeRedis:
    """Redis's strings with their expiry, as the actions use them."""

    def __init__(self):
        self.values = {}
        self.expiry = {}

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.values:
            return None

        self.values[key] = value
        self.expiry[key] = ex

        return True

    async def get(self, key):
        return self.values.get(key)

    def pipeline(self, transaction=True):
        return Pipeline(self)

    async def getdel(self, key):
        self.expiry.pop(key, None)

        return self.values.pop(key, None)


@pytest.fixture
def redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(store, "get_redis", lambda: fake)
    monkeypatch.setattr(actions, "get_redis", lambda: fake)

    async def nothing(*args, **kwargs):
        pass

    async def owned(conversation_id, user_id, token, language):
        return None

    async def companies(token, language):
        return frozenset({COMPANY})

    monkeypatch.setattr(actions, "refuse_if_paused", nothing)
    monkeypatch.setattr(actions, "hit", nothing)
    monkeypatch.setattr(actions.limits, "check", nothing)
    monkeypatch.setattr(actions, "open_conversation", owned)
    monkeypatch.setattr(actions, "user_companies", companies)

    return fake


@pytest.fixture
def writes(monkeypatch):
    """The services' writes, answering 201 with a new company."""
    made = Writes()

    async def send(
        service, method, path, query, body, token, language, idempotency_key=None, via=None
    ):
        made.append((service, method, path, body, token, idempotency_key))
        request = httpx.Request(method, f"http://{service}{path}")

        return httpx.Response(
            made.status,
            json={"id": COMPANY, "name": body["name"], "role": "owner"},
            request=request,
        )

    monkeypatch.setattr(services, "send", send)

    return made
