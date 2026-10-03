import uuid

import pytest
from fastapi import HTTPException
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.integrations import billing
from app.main import app
from app.models.generation import Generation
from app.storage import generations
from tests.unit.test_internal_generations import headers

COMPANY_ID = uuid.uuid4()


@pytest.fixture
def queue(monkeypatch):
    """A signed-in learner, no rate limit, and generations that are recorded, not run."""
    created = []

    async def fake_create(owner_uid, text, kind="preparation", company_id=None, language="en"):
        created.append((owner_uid, kind, company_id))

        return Generation(
            id=uuid.uuid4(), owner_uid=owner_uid, text=text, kind=kind, status="queued"
        )

    monkeypatch.setattr(settings, "generation_limit", 0)
    monkeypatch.setattr(generations, "create", fake_create)
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True
    )

    yield created

    app.dependency_overrides.clear()


def test_a_learner_cannot_start_an_interview_generation(client, queue):
    response = client.post(
        "/generations",
        json={"text": "job", "kind": "interview", "company_id": str(COMPANY_ID)},
    )

    assert response.status_code == 403
    assert queue == []


def test_a_learner_without_preparations_left_is_told_why(client, queue, monkeypatch):
    async def none_left(user_id):
        raise HTTPException(402, "You've used this month's free preparation.")

    monkeypatch.setattr(billing, "use_generation", none_left)

    response = client.post("/generations", json={"text": "Senior Python developer"})

    assert response.status_code == 402
    assert response.json()["detail"] == "You've used this month's free preparation."
    assert queue == []


def test_a_learners_preparation_uses_one_from_billing(client, queue, monkeypatch):
    charged = []

    async def use(user_id):
        charged.append(user_id)

    monkeypatch.setattr(billing, "use_generation", use)

    response = client.post("/generations", json={"text": "Senior Python developer"})

    assert response.status_code == 201
    assert charged == ["ann"]
    assert queue == [("ann", "preparation", None)]


def test_companies_starts_interviews_through_the_internal_route(client, queue):
    response = client.post(
        "/internal/generations",
        json={"text": "Backend engineer", "company_id": str(COMPANY_ID), "owner_uid": "bob"},
        headers=headers(),
    )

    assert response.status_code == 201
    assert queue == [("bob", "interview", COMPANY_ID)]
