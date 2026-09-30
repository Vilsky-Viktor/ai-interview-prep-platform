import uuid
from datetime import UTC, datetime

import pytest

from app.auth import current_user
from app.constants.events import PREPARATION_SHARED
from app.constants.sets import SetKind
from app.main import app
from app.models.sets import QuestionSet
from app.models.sharing import ShareInvite
from app.routers import shares as shares_router
from app.schemas.user import User
from app.storage import preparations, shares

SET_ID = uuid.uuid4()


def sign_in(email, verified=True, uid="user-1"):
    user = User(uid=uid, email=email, email_verified=verified, name="Ann")
    app.dependency_overrides[current_user] = lambda: user


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


def test_owner_shares_and_event_is_published(client, monkeypatch):
    events = []

    async def fake_get(set_id):
        return QuestionSet(id=SET_ID, kind=SetKind.PREPARATION, owner_id="owner", title="Backend")

    async def fake_upsert(set_id, email, invited_by):
        return invite()

    async def fake_publish(event_type, data):
        events.append((event_type, data))

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(shares, "upsert", fake_upsert)
    monkeypatch.setattr(shares_router, "publish", fake_publish)
    sign_in("ann@example.com", uid="owner")

    response = client.post(f"/preparations/{SET_ID}/shares", json={"email": "Bob@example.com"})

    assert response.status_code == 201
    assert events == [
        (
            PREPARATION_SHARED,
            {"email": "bob@example.com", "token": "token-1", "title": "Backend", "inviter": "Ann"},
        )
    ]


def test_only_owner_can_share(client, monkeypatch):
    async def fake_get(set_id):
        return QuestionSet(id=SET_ID, kind=SetKind.PREPARATION, owner_id="owner", title="Backend")

    monkeypatch.setattr(preparations, "get", fake_get)
    sign_in("eve@example.com", uid="eve")

    response = client.post(f"/preparations/{SET_ID}/shares", json={"email": "bob@example.com"})

    assert response.status_code == 404
