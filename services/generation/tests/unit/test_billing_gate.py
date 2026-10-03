import asyncio
import uuid

import pytest
from fastapi import HTTPException
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.integrations import billing
from app.main import app
from app.models.generation import Generation
from app.routers import generations as generations_router
from app.services import pipeline
from app.storage import generations
from tests.unit.test_internal_generations import headers

COMPANY_ID = uuid.uuid4()


@pytest.fixture
def queue(monkeypatch):
    """A signed-in learner, no rate limit, and generations that are recorded, not run."""
    created = []

    async def fake_create(
        owner_uid, text, kind="preparation", company_id=None, language="en", generation_id=None
    ):
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
    async def none_left(user_id, generation_id):
        raise HTTPException(402, "Not enough credits. Top up to continue.")

    monkeypatch.setattr(billing, "hold_kit", none_left)

    response = client.post("/generations", json={"text": "Senior Python developer"})

    assert response.status_code == 402
    assert response.json()["detail"] == "Not enough credits. Top up to continue."
    assert queue == []


def test_a_refused_kit_doesnt_count_towards_the_daily_cap(client, queue, monkeypatch):
    counted = []

    async def none_left(user_id, generation_id):
        raise HTTPException(402, "Not enough credits. Top up to continue.")

    async def count():
        counted.append(1)

    monkeypatch.setattr(billing, "hold_kit", none_left)
    monkeypatch.setattr(generations_router, "use_daily_budget", count)

    assert client.post("/generations", json={"text": "job"}).status_code == 402
    assert counted == []


def test_the_daily_cap_gives_the_kits_credits_back(client, queue, monkeypatch):
    released = []

    async def hold(user_id, generation_id):
        pass

    async def paused():
        raise HTTPException(503, "Paused")

    async def release(generation_id):
        released.append(generation_id)

    monkeypatch.setattr(billing, "hold_kit", hold)
    monkeypatch.setattr(billing, "release_kit", release)
    monkeypatch.setattr(generations_router, "use_daily_budget", paused)

    assert client.post("/generations", json={"text": "job"}).status_code == 503
    assert len(released) == 1
    assert queue == []


def test_a_learners_preparation_uses_one_from_billing(client, queue, monkeypatch):
    charged = []

    async def hold(user_id, generation_id):
        charged.append(user_id)

    monkeypatch.setattr(billing, "hold_kit", hold)

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


def test_a_billing_hiccup_doesnt_fail_a_finished_kit(monkeypatch):
    calls = []

    async def flaky(generation_id):
        calls.append(generation_id)

        if len(calls) < 2:
            raise RuntimeError("billing down")

    async def no_wait(_seconds):
        pass

    monkeypatch.setattr(billing, "charge_kit", flaky)
    monkeypatch.setattr(pipeline.asyncio, "sleep", no_wait)
    kit = uuid.uuid4()

    asyncio.run(pipeline.charge_finished_kit(kit))

    assert calls == [kit, kit]
