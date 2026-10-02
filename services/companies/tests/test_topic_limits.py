import uuid
from datetime import UTC, datetime

from prepza_common.auth import current_user
from prepza_common.user import User

from app.helpers.interviews import pick_questions
from app.integrations import library
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
TOPIC_ID = uuid.uuid4()


def setup(monkeypatch, saved):
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        share_results=False,
        set_id=uuid.uuid4(),
        topic_limits={},
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

    async def fake_set(_set_id):
        return {"topics": [{"id": str(TOPIC_ID), "title": "SQL", "question_count": 10}]}

    async def fake_save(_interview_id, topic_id, limit):
        saved.append((topic_id, limit))

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(library, "get_set", fake_set)
    monkeypatch.setattr(interviews, "set_topic_limit", fake_save)


def test_limit_cannot_exceed_topic_questions(client, monkeypatch):
    saved = []
    setup(monkeypatch, saved)
    url = f"/interviews/{INTERVIEW_ID}/topics/{TOPIC_ID}/limit"

    assert client.put(url, json={"limit": 11}).status_code == 422
    assert client.put(url, json={"limit": 0}).status_code == 422
    assert client.put(url, json={"limit": 5}).status_code == 204
    assert client.put(url, json={"limit": None}).status_code == 204
    assert saved == [(TOPIC_ID, 5), (TOPIC_ID, None)]

    app.dependency_overrides.clear()


def test_unknown_topic_is_not_found(client, monkeypatch):
    setup(monkeypatch, [])
    url = f"/interviews/{INTERVIEW_ID}/topics/{uuid.uuid4()}/limit"

    assert client.put(url, json={"limit": 1}).status_code == 404

    app.dependency_overrides.clear()


def test_pick_questions_takes_a_random_subset():
    questions = list(range(100))
    picked = pick_questions(questions, 5)

    assert len(picked) == 5
    assert len(set(picked)) == 5
    assert set(picked) <= set(questions)
    assert pick_questions(questions, None) == questions
