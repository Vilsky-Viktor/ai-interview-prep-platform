import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import library, rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
SET_ID = uuid.uuid4()
SESSION_ID = uuid.uuid4()


@pytest.fixture
def started(monkeypatch):
    """Bob, a viewer of the company, and one ready test; returns what rounds was asked for."""
    asked = []
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(
            company_id=COMPANY_ID,
            user_id="bob",
            invited_email="bob@example.com",
            role="viewer",
            created_at=datetime.now(UTC),
        )
    ]

    def interview(set_id=SET_ID):
        return Interview(
            id=uuid.uuid4(),
            company_id=COMPANY_ID,
            generation_id=None,
            set_id=set_id,
            question_seconds=45,
            topic_limits={},
        )

    async def get_interview(_interview_id):
        return interview()

    async def get_company(_company_id):
        return company

    async def content(_set_id):
        questions = [{"id": str(uuid.uuid4()), "text": "Q?", "options": []} for _ in range(3)]

        return {"id": str(SET_ID), "topics": [{"id": "t1", "title": "SQL", "questions": questions}]}

    async def create_sessions(payload):
        asked.append(payload)

        return [{"id": str(SESSION_ID), "topic_title": "SQL", "status": "in_progress"}]

    monkeypatch.setattr(interviews, "get", get_interview)
    monkeypatch.setattr(companies, "get", get_company)
    monkeypatch.setattr(library, "get_content", content)
    monkeypatch.setattr(rounds, "create_sessions", create_sessions)
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True
    )

    yield asked

    app.dependency_overrides.clear()


def test_any_member_previews_a_test_as_a_candidate_would_for_free(client, started):
    response = client.post(f"/interviews/{uuid.uuid4()}/preview")

    assert response.status_code == 201
    assert response.json() == {"session_id": str(SESSION_ID)}
    [payload] = started
    # Marked as a preview, timed like the real test, and with no invite behind it to charge.
    assert payload["preview"] is True
    assert payload["question_seconds"] == 45
    assert payload["user_id"] == "bob"
    assert len(payload["topics"][0]["questions"]) == 3


def test_someone_outside_the_company_cant(client, started):
    app.dependency_overrides[current_user] = lambda: User(
        uid="eve", email="eve@example.com", email_verified=True
    )

    assert client.post(f"/interviews/{uuid.uuid4()}/preview").status_code == 404
    assert started == []
