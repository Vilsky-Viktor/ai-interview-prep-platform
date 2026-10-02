import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.models.companies import Company, Member
from app.storage import members

MEMBER_ID = uuid.uuid4()
COMPANY_ID = uuid.uuid4()


def sign_in(email, verified=True, uid="admin"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=verified, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stored_invite(monkeypatch):
    member = Member(
        id=MEMBER_ID,
        company_id=COMPANY_ID,
        invited_email="bob@example.com",
        token="token-1",
        role="admin",
        created_at=datetime.now(UTC),
    )
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    accepted = []

    async def fake_get(token):
        return (member, company) if token == "token-1" else None

    async def fake_accept(item, user_id):
        accepted.append(user_id)

    monkeypatch.setattr(members, "get_by_token", fake_get)
    monkeypatch.setattr(members, "accept", fake_accept)

    return accepted


def test_invited_email_accepts(client, stored_invite):
    sign_in("Bob@Example.com", uid="bob")

    assert client.post("/members/invites/token-1/accept").status_code == 204
    assert stored_invite == ["bob"]


@pytest.mark.parametrize(
    ("email", "verified"), [("eve@example.com", True), ("bob@example.com", False)]
)
def test_other_or_unverified_email_is_rejected(client, stored_invite, email, verified):
    sign_in(email, verified)

    assert client.post("/members/invites/token-1/accept").status_code == 403
    assert stored_invite == []


def test_unknown_token(client, stored_invite):
    sign_in("bob@example.com")

    assert client.post("/members/invites/missing/accept").status_code == 404


def test_invite_view(client, stored_invite):
    sign_in("bob@example.com")
    response = client.get("/members/invites/token-1")

    assert response.status_code == 200
    assert response.json() == {
        "company_name": "Arcolabs",
        "email": "bob@example.com",
        "joined": False,
    }
