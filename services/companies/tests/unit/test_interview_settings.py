import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.audit import AuditAction
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_updates_the_time_per_question(client, monkeypatch, audited):
    sign_in()
    saved = {}
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        set_id=None,
        pass_mark=70,
    )
    company = Company(id=COMPANY_ID, name="My company", created_at=datetime.now(UTC))
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

    async def fake_update(_interview_id, settings):
        saved.update(settings.model_dump())

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(interviews, "update_settings", fake_update)
    url = f"/interviews/{INTERVIEW_ID}/settings"

    response = client.patch(url, json={"question_seconds": 45})

    assert response.status_code == 204
    assert saved == {"question_seconds": 45, "hired": False, "pass_mark": 70}

    client.patch(url, json={"question_seconds": 45, "hired": True, "pass_mark": 70})

    assert saved == {"question_seconds": 45, "hired": True, "pass_mark": 70}
    # Only a changed pass mark is recorded.
    assert audited == []

    client.patch(url, json={"question_seconds": 45, "pass_mark": 80})

    assert audited == [(COMPANY_ID, "bob", AuditAction.PASS_MARK_CHANGED, INTERVIEW_ID)]
    too_short = client.patch(url, json={"question_seconds": 5})

    assert too_short.status_code == 422


def test_a_tests_status_follows_its_candidates_and_the_hired_mark():
    from app.helpers.interviews import interview_status

    assert interview_status(False, 0) == "new"
    assert interview_status(False, 3) == "in_process"
    # Marked as hired wins, with or without candidates.
    assert interview_status(True, 3) == "hired"
    assert interview_status(True, 0) == "hired"
