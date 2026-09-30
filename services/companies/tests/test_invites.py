import uuid
from datetime import UTC, datetime

import pytest

from app.auth import current_user
from app.constants.invites import InviteStatus
from app.main import app
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.schemas.user import User
from app.storage import invites as invite_store

INVITE_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


def sign_in(email, verified=True, uid="cand"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=email, email_verified=verified, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stored_invite(monkeypatch):
    invite = CandidateInvite(
        id=INVITE_ID,
        interview_id=INTERVIEW_ID,
        email="bob@example.com",
        token="token-1",
        status=InviteStatus.INVITED,
        created_at=datetime.now(UTC),
    )
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=uuid.uuid4(),
        generation_id=uuid.uuid4(),
        mode="choice",
        share_results=False,
        set_id=uuid.uuid4(),
    )

    async def fake_get(token):
        return (invite, interview) if token == "token-1" else None

    monkeypatch.setattr(invite_store, "get_by_token", fake_get)

    return invite


@pytest.mark.parametrize(
    ("email", "verified"), [("eve@example.com", True), ("bob@example.com", False)]
)
def test_other_or_unverified_email_is_rejected(client, stored_invite, email, verified):
    sign_in(email, verified)

    assert client.post("/invites/token-1/start").status_code == 403


def test_unknown_token(client, stored_invite):
    sign_in("bob@example.com")

    assert client.post("/invites/missing/start").status_code == 404
