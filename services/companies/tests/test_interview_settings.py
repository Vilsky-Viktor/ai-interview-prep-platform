import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

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


def test_updates_shared_scores(client, monkeypatch):
    sign_in()
    saved = {}
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        share_results=False,
        set_id=None,
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

    response = client.patch(url, json={"share_results": True})

    assert response.status_code == 204
    # Without timer settings, an interview stays untimed with the default limit.
    assert saved == {"share_results": True, "timed": False, "question_seconds": 60}

    response = client.patch(
        url, json={"share_results": False, "timed": True, "question_seconds": 45}
    )

    assert response.status_code == 204
    assert saved == {"share_results": False, "timed": True, "question_seconds": 45}
    too_short = client.patch(url, json={"share_results": False, "question_seconds": 5})

    assert too_short.status_code == 422
