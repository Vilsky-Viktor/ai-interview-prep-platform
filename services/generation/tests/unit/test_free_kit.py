import asyncio
import uuid

import httpx
import pytest
from prepza_common import http
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.constants.generation import FREE_KIT_TOO_MANY_TOPICS, RUN_GENERATION
from app.integrations import billing
from app.main import app
from app.schemas.generation import GenerationOut
from app.services import pipeline
from app.storage import generations
from tests.unit.test_internal_generations import (
    COMPANY_ID,
    GENERATION_ID,
    company_generation,
    headers,
)

REVIEW_URL = f"/generations/{GENERATION_ID}/review"


class FakeClient:
    def __init__(self, response: httpx.Response):
        self.response = response

    async def post(self, url, params=None, headers=None):
        self.response.request = httpx.Request("POST", url)

        return self.response


@pytest.mark.parametrize(
    "response, free",
    [
        (httpx.Response(200, json={"free": True}), True),
        (httpx.Response(200, json={"free": False}), False),
        # A billing that doesn't tell yet.
        (httpx.Response(204), False),
    ],
)
def test_billing_tells_whether_a_kit_is_free(monkeypatch, response, free):
    monkeypatch.setattr(http, "get_client", lambda: FakeClient(response))

    assert asyncio.run(billing.hold_kit("ann", uuid.uuid4())) is free


@pytest.fixture(autouse=True)
def three_free_topics(monkeypatch):
    """The limit's mechanism, whatever FREE_KIT_TOPICS is set to: 3 here, under MAX_TOPICS."""
    monkeypatch.setattr("app.schemas.generation.FREE_KIT_TOPICS", 3)
    monkeypatch.setattr("app.helpers.topics.FREE_KIT_TOPICS", 3)


def preparation(free_kit: bool):
    generation = company_generation()
    generation.kind = "preparation"
    generation.company_id = None
    generation.free_kit = free_kit

    return generation


def test_a_free_kit_includes_fewer_topics():
    free = GenerationOut.model_validate(preparation(True)).model_dump()
    paid = GenerationOut.model_validate(preparation(False)).model_dump()

    assert (free["free_kit"], free["max_topics"]) == (True, 3)
    assert (paid["free_kit"], paid["max_topics"]) == (False, 10)


@pytest.fixture
def review(monkeypatch):
    """A learner reviewing the topics of a generation; returns it to make it free or not."""
    generation = preparation(False)

    async def get(_generation_id):
        return generation

    async def claim(_generation_id):
        return True

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(generations, "claim_review", claim)
    app.dependency_overrides[current_user] = lambda: User(
        uid="alice", email="alice@example.com", email_verified=True
    )

    yield generation

    app.dependency_overrides.clear()


def test_a_free_kit_approves_at_most_three_topics(client, review, queued):
    review.free_kit = True

    refused = client.post(REVIEW_URL, json={"selected": [0, 1, 2, 3]})
    approved = client.post(REVIEW_URL, json={"selected": [0, 1, 2]})

    assert refused.status_code == 422
    assert refused.json()["detail"] == FREE_KIT_TOO_MANY_TOPICS
    assert approved.status_code == 200
    assert len(queued) == 1


def test_a_free_kit_may_ask_to_revise_any_number_of_topics(client, review, queued):
    review.free_kit = True

    response = client.post(
        REVIEW_URL, json={"selected": list(range(5)), "instructions": "Merge the SQL topics"}
    )

    assert response.status_code == 200
    assert queued[0][0] == RUN_GENERATION


def test_a_paid_kit_approves_up_to_ten_topics(client, review):
    assert client.post(REVIEW_URL, json={"selected": list(range(10))}).status_code == 200


def test_a_company_interview_isnt_limited_like_a_free_kit(client, monkeypatch, queued):
    async def get(_generation_id):
        return company_generation()

    async def claim(_generation_id):
        return True

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(generations, "claim_review", claim)

    response = client.post(
        f"/internal/generations/{GENERATION_ID}/review",
        params={"company_id": str(COMPANY_ID)},
        json={"selected": [0, 1, 2, 3]},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["max_topics"] == 10


def test_a_learners_free_kit_is_saved_as_free(client, monkeypatch):
    saved = []

    async def hold(user_id, generation_id):
        return True

    async def create(owner_uid, text, kind, company_id, language, generation_id, free_kit):
        saved.append(free_kit)
        generation = preparation(free_kit)
        generation.id = generation_id

        return generation

    monkeypatch.setattr(settings, "generation_limit", 0)
    monkeypatch.setattr(billing, "hold_kit", hold)
    monkeypatch.setattr(generations, "create", create)
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True
    )

    response = client.post("/generations", json={"text": "Senior Python developer"})
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["max_topics"] == 3
    assert saved == [True]


def test_the_worker_never_approves_too_many_topics_for_a_free_kit():
    approve = {"selected": [0, 1, 2, 3], "instructions": ""}

    with pytest.raises(ValueError, match="free kit"):
        asyncio.run(pipeline.run_pipeline(None, preparation(True), approve))


@pytest.mark.parametrize("was_free,now_free", [(True, False), (False, True), (True, True)])
def test_a_retry_keeps_the_kit_as_billing_holds_it(monkeypatch, was_free, now_free):
    from app.services import retry

    saved = []

    async def fake_hold(user_id, generation_id):
        return now_free

    async def fake_claim(generation_id):
        return True

    async def fake_update(generation_id, **values):
        saved.append(values)

    async def fake_enqueue(*args):
        pass

    async def fake_get(generation_id):
        return None

    monkeypatch.setattr(billing, "hold_kit", fake_hold)
    monkeypatch.setattr(generations, "claim_retry", fake_claim)
    monkeypatch.setattr(generations, "update", fake_update)
    monkeypatch.setattr(generations, "get", fake_get)
    monkeypatch.setattr(retry.tasks, "enqueue", fake_enqueue)

    asyncio.run(retry.retry_generation(preparation(was_free)))

    # Saved only when it changed: a free kit used elsewhere meanwhile makes the retry paid.
    assert saved == ([] if was_free == now_free else [{"free_kit": now_free}])
