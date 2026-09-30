import uuid
from datetime import UTC, datetime

import pytest

from app.auth import current_user
from app.constants.invites import InviteStatus
from app.integrations import rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.schemas.user import User
from app.storage import companies, interviews
from app.storage import invites as invite_store

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
INVITE_ID = uuid.uuid4()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_finished_interview_status(client, monkeypatch):
    sign_in()
    saved = {}
    invite = CandidateInvite(
        id=INVITE_ID,
        interview_id=INTERVIEW_ID,
        email="viktor2@gmail.com",
        token="token-1",
        status=InviteStatus.IN_PROCESS,
        created_at=datetime.now(UTC),
    )
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        mode="choice",
        share_results=False,
        set_id=uuid.uuid4(),
    )
    interview.invites = [invite]
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    company.members = [
        Member(
            company_id=COMPANY_ID,
            user_id="bob",
            invited_email="bob@example.com",
            role="owner",
            created_at=datetime.now(UTC),
        )
    ]

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_scores(_invite_ids):
        return {str(INVITE_ID): {"progress": 40, "grade": 80, "finished": True}}

    async def fake_set(invite_ids, status):
        saved["ids"] = invite_ids
        saved["status"] = status

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(rounds, "invite_scores", fake_scores)
    monkeypatch.setattr(invite_store, "set_status", fake_set)

    response = client.get(f"/interviews/{INTERVIEW_ID}/candidates")

    assert response.status_code == 200
    assert response.json()[0]["status"] == "finished"
    assert saved == {"ids": [INVITE_ID], "status": "finished"}
