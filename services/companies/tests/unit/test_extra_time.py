import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.audit import AuditAction
from app.constants.invites import InviteStatus
from app.helpers.candidates import candidate_seconds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage import companies, interviews, invites

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


@pytest.fixture
def candidate(monkeypatch):
    interview = Interview(id=INTERVIEW_ID, company_id=COMPANY_ID, question_seconds=60)
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="admin")
    ]
    invite = CandidateInvite(
        id=uuid.uuid4(), interview_id=INTERVIEW_ID, email="ann@example.com", extra_time=0
    )
    invite.status = InviteStatus.INVITED
    saved = {}

    async def fake_interview(_id):
        return interview

    async def fake_company(_id):
        return company

    async def fake_invite(_id):
        return invite

    async def fake_set(invite_id, extra_time):
        saved["extra_time"] = extra_time

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(invites, "get", fake_invite)
    monkeypatch.setattr(invites, "set_extra_time", fake_set)
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True
    )

    yield invite, saved

    app.dependency_overrides.clear()


def url(invite):
    return f"/interviews/{INTERVIEW_ID}/candidates/{invite.id}/extra-time"


def test_extra_time_lengthens_each_question():
    assert candidate_seconds(60, 0) == 60
    assert candidate_seconds(60, 50) == 90
    assert candidate_seconds(45, 25) == 56
    assert candidate_seconds(60, None) == 60


def test_a_company_sets_extra_time_before_the_candidate_starts(client, candidate, audited):
    invite, saved = candidate

    assert client.put(url(invite), json={"extra_time": 50}).status_code == 204
    assert saved == {"extra_time": 50}
    assert audited == [(COMPANY_ID, "bob", AuditAction.EXTRA_TIME_SET, invite.id)]
    # Only the offered amounts.
    assert client.put(url(invite), json={"extra_time": 30}).status_code == 422

    invite.status = InviteStatus.IN_PROCESS

    assert client.put(url(invite), json={"extra_time": 100}).status_code == 409
