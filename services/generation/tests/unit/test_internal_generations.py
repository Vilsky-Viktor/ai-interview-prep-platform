import uuid

import pytest
from pydantic import ValidationError

from app.constants.generation import RUN_GENERATION
from app.main import app
from app.models.generation import Generation
from app.routers import internal
from app.schemas.generation import ReviewRequest
from app.service_auth import service_token
from app.storage import generations

COMPANY_ID = uuid.uuid4()
GENERATION_ID = uuid.uuid4()


def headers():
    return {"Authorization": f"Bearer {service_token('generation')}"}


def company_generation():
    return Generation(
        id=GENERATION_ID,
        owner_uid="alice",
        kind="interview",
        company_id=COMPANY_ID,
        text="Job description",
        language="en",
        status="awaiting_review",
        topics=[{"main_topic": "Python", "subtopics": ["asyncio"]}],
        progress=None,
        preparation_id=None,
        error=None,
    )


def fake_get(monkeypatch):
    async def get(_generation_id):
        return company_generation()

    monkeypatch.setattr(generations, "get", get)


def test_company_generation_is_visible_to_its_company(client, monkeypatch):
    fake_get(monkeypatch)
    response = client.get(
        f"/internal/generations/{GENERATION_ID}",
        params={"company_id": str(COMPANY_ID)},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "awaiting_review"


def test_company_generation_is_hidden_from_another_company(client, monkeypatch):
    fake_get(monkeypatch)
    response = client.get(
        f"/internal/generations/{GENERATION_ID}",
        params={"company_id": str(uuid.uuid4())},
        headers=headers(),
    )

    assert response.status_code == 404


def test_internal_generation_needs_a_service_token(client):
    response = client.get(
        f"/internal/generations/{GENERATION_ID}", params={"company_id": str(COMPANY_ID)}
    )

    assert response.status_code in (401, 403)


def test_company_review_queues_the_topics(client, monkeypatch):
    fake_get(monkeypatch)
    reviewed = []

    async def fake_submit(generation, body):
        reviewed.append(body.selected)
        generation.status = "queued"

        return generation

    monkeypatch.setattr(internal, "submit_review", fake_submit)
    response = client.post(
        f"/internal/generations/{GENERATION_ID}/review",
        params={"company_id": str(COMPANY_ID)},
        json={"selected": [0], "instructions": ""},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert reviewed == [[0]]


def test_only_a_failed_generation_is_retried(client, monkeypatch, queued):
    fake_get(monkeypatch)
    claims = iter([True, False])

    async def fake_claim(_generation_id):
        return next(claims)

    monkeypatch.setattr(generations, "claim_retry", fake_claim)
    url = f"/internal/generations/{GENERATION_ID}/retry"
    params = {"company_id": str(COMPANY_ID)}

    assert client.post(url, params=params, headers=headers()).status_code == 200
    assert client.post(url, params=params, headers=headers()).status_code == 409
    assert queued == [(RUN_GENERATION, {"generation_id": str(GENERATION_ID)})]


def test_approving_more_than_max_topics_is_rejected(client, monkeypatch):
    fake_get(monkeypatch)
    url = f"/internal/generations/{GENERATION_ID}/review"
    params = {"company_id": str(COMPANY_ID)}
    eleven = list(range(11))

    approve = client.post(
        url, params=params, json={"selected": eleven, "instructions": ""}, headers=headers()
    )

    assert approve.status_code == 422
    assert "at most 10 topics" in approve.text


def test_more_than_max_topics_is_fine_with_instructions_to_revise(client, monkeypatch):
    fake_get(monkeypatch)
    revised = []

    async def fake_submit(generation, body):
        revised.append(len(body.selected))

        return generation

    monkeypatch.setattr(internal, "submit_review", fake_submit)
    response = client.post(
        f"/internal/generations/{GENERATION_ID}/review",
        params={"company_id": str(COMPANY_ID)},
        json={"selected": list(range(11)), "instructions": "Merge the two SQL topics"},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["max_topics"] == 10
    assert revised == [11]


def test_lists_unfinished_preparations_with_a_short_preview(client, monkeypatch):
    from datetime import UTC, datetime

    from prepza_common.auth import current_user
    from prepza_common.user import User

    waiting = company_generation()
    waiting.kind = "preparation"
    waiting.text = "  Senior accountant\n\nat Acme. " + "x" * 300
    waiting.created_at = datetime.now(UTC)

    async def fake_list(owner_uid, offset, limit):
        assert owner_uid == "alice"

        return [waiting]

    monkeypatch.setattr(generations, "list_unfinished", fake_list)
    app.dependency_overrides[current_user] = lambda: User(
        uid="alice", email="alice@example.com", email_verified=True
    )

    [row] = client.get("/generations").json()

    assert row["status"] == "awaiting_review"
    assert row["preview"].startswith("Senior accountant at Acme. xx")
    assert row["preview"].endswith("…")
    assert len(row["preview"]) == 121

    app.dependency_overrides.clear()


def owned_preparation(monkeypatch, status="running"):
    from prepza_common.auth import current_user
    from prepza_common.user import User

    generation = company_generation()
    generation.kind = "preparation"
    generation.company_id = None
    generation.status = status

    async def get(_generation_id):
        return generation

    monkeypatch.setattr(generations, "get", get)
    app.dependency_overrides[current_user] = lambda: User(
        uid="alice", email="alice@example.com", email_verified=True
    )

    return generation


def test_owner_cancels_an_unfinished_preparation(client, monkeypatch):
    generation = owned_preparation(monkeypatch)
    claims = iter([True, False])

    async def fake_cancel(_generation_id):
        claimed = next(claims)

        if claimed:
            generation.status = "cancelled"

        return claimed

    async def release(_generation_id):
        return None

    monkeypatch.setattr(generations, "cancel", fake_cancel)
    monkeypatch.setattr("app.services.cancel.billing.release_kit", release)
    url = f"/generations/{GENERATION_ID}/cancel"

    first = client.post(url)
    again = client.post(url)

    assert first.status_code == 200
    assert first.json()["status"] == "cancelled"
    assert again.status_code == 409

    app.dependency_overrides.clear()


def test_interview_generations_are_not_cancelled_here(client, monkeypatch):
    generation = owned_preparation(monkeypatch)
    generation.kind = "interview"

    assert client.post(f"/generations/{GENERATION_ID}/cancel").status_code == 409

    app.dependency_overrides.clear()


def test_company_cancels_its_interview_generation(client, monkeypatch):
    generation = company_generation()

    async def get(_generation_id):
        return generation

    async def fake_cancel(_generation_id):
        generation.status = "cancelled"

        return True

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(generations, "cancel", fake_cancel)
    url = f"/internal/generations/{GENERATION_ID}/cancel"

    other = client.post(url, params={"company_id": str(uuid.uuid4())}, headers=headers())
    own = client.post(url, params={"company_id": str(COMPANY_ID)}, headers=headers())

    assert other.status_code == 404
    assert own.status_code == 200
    assert own.json()["status"] == "cancelled"


def test_a_blank_edited_topic_is_rejected():
    with pytest.raises(ValidationError):
        ReviewRequest(selected=[0], topics=[{"main_topic": "  ", "subtopics": []}])

    review = ReviewRequest(selected=[0], topics=[{"main_topic": " SQL ", "subtopics": [" Joins "]}])

    assert review.topics[0].model_dump() == {"main_topic": "SQL", "subtopics": ["Joins"]}
