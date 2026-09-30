import uuid
from datetime import UTC, datetime

import httpx

from app.auth import current_user
from app.integrations import generation
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.schemas.user import User
from app.storage import companies, interviews

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
GENERATION_ID = uuid.uuid4()


def sign_in(uid):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name=uid
    )


def setup(monkeypatch, role):
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=GENERATION_ID,
        mode="open",
        share_results=False,
        set_id=None,
        invites=[],
    )
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="alice", invited_email="alice@example.com", role="owner"),
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role=role),
    ]

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)


def test_admin_who_did_not_start_it_sees_the_generation(client, monkeypatch):
    """The generation belongs to alice, but bob is in the same company."""
    setup(monkeypatch, "admin")
    sign_in("bob")
    calls = []

    async def fake_get(generation_id, company_id):
        calls.append((generation_id, company_id))

        return {"id": str(generation_id), "status": "awaiting_review"}

    monkeypatch.setattr(generation, "get", fake_get)
    response = client.get(f"/interviews/{INTERVIEW_ID}/generation")

    assert response.status_code == 200
    assert calls == [(GENERATION_ID, COMPANY_ID)]

    app.dependency_overrides.clear()


def test_outsider_does_not_see_the_generation(client, monkeypatch):
    setup(monkeypatch, "admin")
    sign_in("mallory")

    assert client.get(f"/interviews/{INTERVIEW_ID}/generation").status_code == 404

    app.dependency_overrides.clear()


def test_only_managers_review_topics(client, monkeypatch):
    sign_in("bob")
    calls = []

    async def fake_review(generation_id, company_id, body):
        calls.append(body)

        return httpx.Response(
            200,
            json={"id": str(generation_id), "status": "queued"},
            request=httpx.Request("POST", "http://generation"),
        )

    monkeypatch.setattr(generation, "review", fake_review)
    url = f"/interviews/{INTERVIEW_ID}/generation/review"
    body = {"selected": [0, 2], "instructions": ""}

    for role, expected in (("viewer", 403), ("admin", 200)):
        setup(monkeypatch, role)

        assert client.post(url, json=body).status_code == expected

    assert calls == [body]

    app.dependency_overrides.clear()


def test_second_review_passes_the_conflict_through(client, monkeypatch):
    setup(monkeypatch, "admin")
    sign_in("bob")

    async def fake_review(generation_id, company_id, body):
        return httpx.Response(409, json={"detail": "Generation is not awaiting review"})

    monkeypatch.setattr(generation, "review", fake_review)
    response = client.post(
        f"/interviews/{INTERVIEW_ID}/generation/review", json={"selected": [0]}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Generation is not awaiting review"

    app.dependency_overrides.clear()


def test_only_managers_retry(client, monkeypatch):
    sign_in("bob")
    calls = []

    async def fake_retry(generation_id, company_id):
        calls.append(generation_id)

        return httpx.Response(
            200,
            json={"id": str(generation_id), "status": "queued"},
            request=httpx.Request("POST", "http://generation"),
        )

    monkeypatch.setattr(generation, "retry", fake_retry)
    url = f"/interviews/{INTERVIEW_ID}/generation/retry"

    for role, expected in (("viewer", 403), ("admin", 200)):
        setup(monkeypatch, role)

        assert client.post(url).status_code == expected

    assert calls == [GENERATION_ID]

    app.dependency_overrides.clear()
