import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.constants.sets import SetKind
from app.main import app
from app.models.sets import QuestionSet
from app.models.sharing import ShareInvite
from app.routers import shares as shares_router
from app.services import outbox as outbox_service
from app.storage import preparations, shares
from tests.unit.fake_redis import FakeRedis

SET_ID = uuid.uuid4()


def sign_in(email, verified=True, uid="user-1"):
    user = User(uid=uid, email=email, email_verified=verified, name="Ann")
    app.dependency_overrides[current_user] = lambda: user


@pytest.fixture(autouse=True)
def few_shares(monkeypatch):
    """The kit is shared with nobody yet, unless a test says otherwise."""

    async def not_invited(set_id, email):
        return False

    async def none(set_id):
        return 0

    monkeypatch.setattr(shares, "is_invited", not_invited)
    monkeypatch.setattr(shares, "count_for_set", none)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def invite(accepted_by=None):
    return ShareInvite(
        id=uuid.uuid4(),
        set_id=SET_ID,
        email="bob@example.com",
        token="token-1",
        invited_by="owner",
        accepted_by=accepted_by,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def stored_invite(monkeypatch):
    found = invite()
    accepted = []

    async def fake_get_by_token(token):
        return (found, QuestionSet(id=SET_ID, title="Backend")) if token == "token-1" else None

    async def fake_accept(item, user_id):
        accepted.append(user_id)

    monkeypatch.setattr(shares, "get_by_token", fake_get_by_token)
    monkeypatch.setattr(shares, "accept", fake_accept)

    return accepted


def test_invited_email_accepts(client, stored_invite):
    sign_in("Bob@Example.com", uid="bob")

    assert client.post("/shares/token-1/accept").status_code == 204
    assert stored_invite == ["bob"]


@pytest.mark.parametrize(
    ("email", "verified"), [("eve@example.com", True), ("bob@example.com", False)]
)
def test_other_or_unverified_email_is_rejected(client, stored_invite, email, verified):
    sign_in(email, verified)

    assert client.post("/shares/token-1/accept").status_code == 403
    assert stored_invite == []


def test_unknown_token(client, stored_invite):
    sign_in("bob@example.com")

    assert client.post("/shares/missing/accept").status_code == 404


def test_owner_shares_and_the_email_event_is_saved_with_the_invite(client, monkeypatch):
    saved = []
    flushed = []

    async def fake_get(set_id):
        return QuestionSet(id=SET_ID, kind=SetKind.PREPARATION, owner_id="owner", title="Backend")

    async def fake_upsert(set_id, email, invited_by, title, inviter):
        saved.append((email, invited_by, title, inviter))

        return invite()

    async def fake_flush():
        flushed.append(True)

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(shares, "upsert", fake_upsert)
    monkeypatch.setattr(outbox_service, "flush_quietly", fake_flush)
    monkeypatch.setattr(shares_router, "get_redis", FakeRedis)
    sign_in("ann@example.com", uid="owner")

    response = client.post(f"/preparations/{SET_ID}/shares", json={"email": "Bob@example.com"})

    assert response.status_code == 201
    # The storage saves the event in the invite's transaction; it's published right after.
    assert saved == [("bob@example.com", "owner", "Backend", "Ann")]
    assert flushed == [True]


def test_only_owner_can_share(client, monkeypatch):
    async def fake_get(set_id):
        return QuestionSet(id=SET_ID, kind=SetKind.PREPARATION, owner_id="owner", title="Backend")

    monkeypatch.setattr(preparations, "get", fake_get)
    sign_in("eve@example.com", uid="eve")

    response = client.post(f"/preparations/{SET_ID}/shares", json={"email": "bob@example.com"})

    assert response.status_code == 404


def test_a_sender_is_limited_per_hour(client, monkeypatch):
    redis = FakeRedis()

    async def fake_get(set_id):
        return QuestionSet(id=SET_ID, kind=SetKind.PREPARATION, owner_id="owner", title="Backend")

    async def fake_upsert(set_id, email, invited_by, title, inviter):
        return invite()

    async def no_flush():
        pass

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(shares, "upsert", fake_upsert)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)
    monkeypatch.setattr(shares_router, "get_redis", lambda: redis)
    monkeypatch.setattr(settings, "email_hourly_limit", 2)
    sign_in("ann@example.com", uid="owner")
    url = f"/preparations/{SET_ID}/shares"

    codes = [client.post(url, json={"email": f"user{i}@example.com"}).status_code for i in range(3)]

    assert codes == [201, 201, 429]
    # Companies count against the same limit, as both use these keys.
    assert redis.counts["rate:emails:hour:owner"] == 3


def test_a_kit_is_shared_with_at_most_30_people_but_resends_still_work(client, monkeypatch):
    owned = QuestionSet(id=uuid.uuid4(), kind=SetKind.PREPARATION, owner_id="user-1", title="Kit")
    sent = []

    async def fake_get(set_id):
        return owned

    async def thirty(set_id):
        return 30

    async def invited(set_id, email):
        return email == "old@example.com"

    async def fake_upsert(set_id, email, invited_by, title, inviter):
        sent.append(email)

        return ShareInvite(email=email, created_at=datetime.now(UTC))

    async def no_flush():
        pass

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(shares, "count_for_set", thirty)
    monkeypatch.setattr(shares, "is_invited", invited)
    monkeypatch.setattr(shares, "upsert", fake_upsert)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)
    monkeypatch.setattr(shares_router, "get_redis", lambda: FakeRedis())
    sign_in("owner@example.com")
    url = f"/preparations/{owned.id}/shares"

    new = client.post(url, json={"email": "new@example.com"})
    resent = client.post(url, json={"email": "old@example.com"})

    assert new.status_code == 429
    assert new.json()["detail"] == "A kit can be shared with at most 30 people."
    assert resent.status_code == 201
    assert sent == ["old@example.com"]
