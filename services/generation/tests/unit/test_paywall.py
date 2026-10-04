import asyncio

import pytest
from fastapi import HTTPException
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.generation import RUN_GENERATION
from app.integrations import billing
from app.main import app
from app.services import review as review_service
from app.storage import generations
from tests.unit.test_internal_generations import (
    COMPANY_ID,
    GENERATION_ID,
    company_generation,
    headers,
)

REVIEW_URL = f"/generations/{GENERATION_ID}/review"
NOT_ENOUGH = "Not enough credits. Top up to continue."


def preparation(approved: bool = False):
    generation = company_generation()
    generation.kind = "preparation"
    generation.company_id = None
    generation.approved = approved

    return generation


@pytest.fixture
def billed(monkeypatch):
    """Billing and the generation's row, recorded: holds, releases and updates."""
    calls = {"holds": [], "releases": [], "updates": [], "counted": 0}

    async def hold(user_id, generation_id):
        calls["holds"].append(generation_id)

    async def release(generation_id):
        calls["releases"].append(generation_id)

    async def update(generation_id, **values):
        calls["updates"].append(values)

    async def count():
        calls["counted"] += 1

    async def claim(_generation_id):
        return True

    monkeypatch.setattr(billing, "hold_kit", hold)
    monkeypatch.setattr(billing, "release_kit", release)
    monkeypatch.setattr(generations, "update", update)
    monkeypatch.setattr(generations, "claim_review", claim)
    monkeypatch.setattr(review_service, "use_daily_budget", count)

    return calls


@pytest.fixture
def learner(monkeypatch):
    generation = preparation()

    async def get(_generation_id):
        return generation

    monkeypatch.setattr(generations, "get", get)
    app.dependency_overrides[current_user] = lambda: User(
        uid="alice", email="alice@example.com", email_verified=True
    )

    yield generation

    app.dependency_overrides.clear()


def test_approving_a_learners_topics_pays_for_the_kit(client, learner, billed, queued):
    response = client.post(REVIEW_URL, json={"selected": [0, 1, 2]})

    assert response.status_code == 200
    assert billed["holds"] == [GENERATION_ID]
    assert billed["counted"] == 1
    assert {"approved": True} in billed["updates"]
    assert queued[0][0] == RUN_GENERATION


def test_revising_the_topics_is_free(client, learner, billed, queued):
    response = client.post(
        REVIEW_URL, json={"selected": [0, 1], "instructions": "Merge the SQL topics"}
    )

    assert response.status_code == 200
    assert billed["holds"] == []
    assert billed["counted"] == 0
    assert len(queued) == 1


def test_without_enough_credits_the_draft_waits_for_a_top_up(
    client, learner, billed, queued, monkeypatch
):
    async def none_left(user_id, generation_id):
        raise HTTPException(402, NOT_ENOUGH)

    monkeypatch.setattr(billing, "hold_kit", none_left)

    response = client.post(REVIEW_URL, json={"selected": [0]})

    assert response.status_code == 402
    assert response.json()["detail"] == NOT_ENOUGH
    # Back to review, not counted against the day's cap, nothing queued.
    assert billed["updates"] == [{"status": "awaiting_review"}]
    assert billed["counted"] == 0
    assert queued == []


def test_the_daily_cap_gives_the_credits_back_and_keeps_the_draft(
    client, learner, billed, queued, monkeypatch
):
    async def paused():
        raise HTTPException(503, "Paused")

    monkeypatch.setattr(review_service, "use_daily_budget", paused)

    response = client.post(REVIEW_URL, json={"selected": [0]})

    assert response.status_code == 503
    assert billed["releases"] == [GENERATION_ID]
    assert billed["updates"] == [{"status": "awaiting_review"}]
    assert queued == []


def test_approving_an_interview_charges_nothing(client, billed, queued, monkeypatch):
    async def get(_generation_id):
        return company_generation()

    monkeypatch.setattr(generations, "get", get)

    response = client.post(
        f"/internal/generations/{GENERATION_ID}/review",
        params={"company_id": str(COMPANY_ID)},
        json={"selected": [0, 1, 2, 3]},
        headers=headers(),
    )

    assert response.status_code == 200
    assert billed["holds"] == []
    assert len(queued) == 1


@pytest.mark.parametrize("approved", [True, False])
def test_a_retry_pays_again_only_after_approval(monkeypatch, billed, approved):
    from app.services import retry

    async def claim(_generation_id):
        return True

    async def get(_generation_id):
        return None

    monkeypatch.setattr(generations, "claim_retry", claim)
    monkeypatch.setattr(generations, "get", get)

    asyncio.run(retry.retry_generation(preparation(approved)))

    # A kit that failed while drafting its topics hasn't been paid for yet.
    assert billed["holds"] == ([GENERATION_ID] if approved else [])
