import pytest

from app.storage import session_expiry


@pytest.fixture(autouse=True)
def nothing_expired(monkeypatch):
    """Opening a session checks whether the whole interview ran out of time, in the database;
    unit tests have none, so nothing has expired unless a test says so."""

    async def none_expired(now, limit, invite_id=None):
        return []

    monkeypatch.setattr(session_expiry, "expired_invites", none_expired)


@pytest.fixture(autouse=True)
def no_rate_limits(monkeypatch):
    """Rate limits count in Redis, which unit tests don't have; a test that checks them
    replaces `hit` itself."""

    async def allowed(redis, key, limit, window):
        return None

    monkeypatch.setattr("app.routers.help.hit", allowed)
    monkeypatch.setattr("app.routers.practice.hit", allowed)


@pytest.fixture(autouse=True)
def help_spending(monkeypatch):
    """The help chat's token budget, without Redis: every amount spent, in order."""
    spent = []

    async def spend(redis, key, amount, limit, window, message=None):
        spent.append((key, amount))

    monkeypatch.setattr("app.routers.help.spend", spend)
    monkeypatch.setattr("app.services.help.add_spent", spend)

    return spent
