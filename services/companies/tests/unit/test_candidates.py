import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.invites import InviteStatus
from app.integrations import billing, rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
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


@pytest.fixture(autouse=True)
def no_billing(monkeypatch):
    async def done(_key):
        return None

    monkeypatch.setattr(billing, "charge_candidate", done)
    monkeypatch.setattr(billing, "release_candidate", done)


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
    asked = []

    async def fake_invites(interview_id, offset, limit):
        asked.append((interview_id, offset, limit))

        return [invite]

    monkeypatch.setattr(invite_store, "list_for_interview", fake_invites)

    response = client.get(f"/interviews/{INTERVIEW_ID}/candidates?sort=date&offset=20&limit=20")

    assert response.status_code == 200
    assert response.json()[0]["status"] == "finished"
    assert saved == {"ids": [INVITE_ID], "status": "finished"}
    assert asked == [(INTERVIEW_ID, 20, 20)]


def revoke(client, monkeypatch, status):
    sign_in()
    removed = []
    invite = CandidateInvite(
        id=INVITE_ID,
        interview_id=INTERVIEW_ID,
        email="cand@example.com",
        token="token-2",
        status=status,
        created_at=datetime.now(UTC),
    )
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
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

    async def fake_remove(invite_id):
        removed.append(invite_id)

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(invite_store, "remove", fake_remove)
    response = client.delete(f"/interviews/{INTERVIEW_ID}/candidates/{INVITE_ID}")

    return response.status_code, removed


def test_an_unused_invite_is_revoked(client, monkeypatch):
    assert revoke(client, monkeypatch, InviteStatus.INVITED) == (204, [INVITE_ID])


def test_a_started_invite_is_kept(client, monkeypatch):
    assert revoke(client, monkeypatch, InviteStatus.IN_PROCESS) == (409, [])


def test_candidates_are_sorted_by_grade_by_default(client, monkeypatch):
    sign_in()
    interview = Interview(
        id=INTERVIEW_ID, company_id=COMPANY_ID, generation_id=uuid.uuid4(), set_id=uuid.uuid4()
    )
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="owner")
    ]
    # Newest first, as storage lists them: Cleo has no grade yet, Ben 60, Ada 90.
    grades = {"cleo": None, "ben": 60, "ada": 90}
    everyone = [
        CandidateInvite(
            id=uuid.uuid4(),
            interview_id=INTERVIEW_ID,
            email=f"{name}@example.com",
            token=f"token-{name}",
            status="in_process",
            created_at=datetime.now(UTC),
        )
        for name in grades
    ]
    totals = {
        str(invite.id): {"progress": 50, "grade": grade, "finished": False}
        for invite, grade in zip(everyone, grades.values(), strict=True)
    }

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_all(_interview_id):
        return everyone

    async def fake_scores(invite_ids):
        return {str(invite_id): totals[str(invite_id)] for invite_id in invite_ids}

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(invite_store, "list_all_for_interview", fake_all)
    monkeypatch.setattr(rounds, "invite_scores", fake_scores)

    first = client.get(f"/interviews/{INTERVIEW_ID}/candidates?offset=0&limit=2").json()
    second = client.get(f"/interviews/{INTERVIEW_ID}/candidates?offset=2&limit=2").json()

    assert [row["email"] for row in first] == ["ada@example.com", "ben@example.com"]
    assert [row["email"] for row in second] == ["cleo@example.com"]
    assert second[0]["grade"] is None
