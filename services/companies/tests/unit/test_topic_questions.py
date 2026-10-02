import uuid
from datetime import UTC, datetime

import httpx
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import generation, library
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
TOPIC_ID = uuid.uuid4()
QUESTION_ID = uuid.uuid4()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )


def interview_and_company(role):
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        share_results=False,
        set_id=uuid.uuid4(),
    )
    company = Company(id=COMPANY_ID, name="My company", created_at=datetime.now(UTC))
    company.members = [
        Member(
            company_id=COMPANY_ID,
            user_id="bob",
            invited_email="bob@example.com",
            role=role,
            created_at=datetime.now(UTC),
        )
    ]

    return interview, company


def test_only_owner_or_admin_can_regenerate(client, monkeypatch):
    sign_in()
    calls = []

    async def fake_regenerate(question_id, set_id, user_id):
        calls.append(user_id)

        return httpx.Response(200, json={"id": str(QUESTION_ID), "text": "New question?"})

    monkeypatch.setattr(generation, "regenerate_question", fake_regenerate)
    url = f"/interviews/{INTERVIEW_ID}/questions/{QUESTION_ID}/regenerate"

    for role, expected in (("viewer", 403), ("admin", 200), ("owner", 200)):
        interview, company = interview_and_company(role)

        async def fake_interview(_interview_id, interview=interview):
            return interview

        async def fake_company(_company_id, company=company):
            return company

        monkeypatch.setattr(interviews, "get", fake_interview)
        monkeypatch.setattr(companies, "get", fake_company)

        assert client.post(url).status_code == expected

    assert calls == ["bob", "bob"]

    app.dependency_overrides.clear()


def test_only_owner_or_admin_reads_reports(client, monkeypatch):
    sign_in()

    async def fake_reports(_set_id, _question_id, page):
        return [
            {
                "id": str(uuid.uuid4()),
                "reason": "unclear",
                "comment": "",
                "created_at": datetime.now(UTC).isoformat(),
            }
        ]

    monkeypatch.setattr(library, "get_question_reports", fake_reports)
    url = f"/interviews/{INTERVIEW_ID}/questions/{QUESTION_ID}/reports"

    for role, expected in (("viewer", 403), ("admin", 200)):
        interview, company = interview_and_company(role)

        async def fake_interview(_interview_id, interview=interview):
            return interview

        async def fake_company(_company_id, company=company):
            return company

        monkeypatch.setattr(interviews, "get", fake_interview)
        monkeypatch.setattr(companies, "get", fake_company)

        assert client.get(url).status_code == expected

    app.dependency_overrides.clear()


def test_topic_questions_are_text_only(client, monkeypatch):
    sign_in()
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        share_results=False,
        set_id=uuid.uuid4(),
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

    async def fake_questions(set_id, _topic_id):
        assert set_id == interview.set_id

        return [
            {
                "id": str(QUESTION_ID),
                "text": "Explain indexes.",
                "likes": 3,
                "dislikes": 1,
                "reports": 0,
            }
        ]

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(library, "get_topic_questions", fake_questions)

    response = client.get(f"/interviews/{INTERVIEW_ID}/topics/{TOPIC_ID}/questions")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(QUESTION_ID),
            "text": "Explain indexes.",
            "likes": 3,
            "dislikes": 1,
            "reports": 0,
        }
    ]

    app.dependency_overrides.clear()
