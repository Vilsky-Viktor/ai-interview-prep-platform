import asyncio
import uuid

import pytest
from prepza_common.auth import current_user
from prepza_common.constants import LANGUAGES
from prepza_common.user import User

from app.config.settings import settings
from app.integrations import billing
from app.main import app
from app.models.generation import Generation
from app.services import pipeline
from app.storage import generations
from tests.unit.test_internal_generations import headers

COMPANY_ID = uuid.uuid4()


@pytest.fixture
def queue(monkeypatch):
    """A signed-in learner, no rate limit, and generations that are recorded, not run."""
    created = []

    async def fake_create(
        owner_uid,
        text,
        kind="preparation",
        company_id=None,
        language="en",
        generation_id=None,
    ):
        created.append((owner_uid, kind, company_id, language))

        return Generation(
            id=uuid.uuid4(),
            owner_uid=owner_uid,
            text=text,
            kind=kind,
            status="queued",
            language=language,
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


def test_starting_a_kit_is_free_and_never_touches_billing(client, queue, monkeypatch):
    async def never(*_args):
        raise AssertionError("billing was asked")

    monkeypatch.setattr(billing, "hold_kit", never)

    response = client.post("/generations", json={"text": "Senior Python developer"})

    assert response.status_code == 201
    assert queue == [("ann", "preparation", None, "en")]


def test_a_kit_is_written_in_its_texts_language_not_the_interfaces(client, queue):
    # A Russian interface, hiring for an English-speaking role.
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True, language="ru"
    )

    response = client.post("/generations", json={"text": "Senior Python developer, remote"})

    assert response.json()["language"] == "en"
    assert queue == [("ann", "preparation", None, "en")]


def test_companies_starts_interviews_through_the_internal_route(client, queue):
    response = client.post(
        "/internal/generations",
        # A recruiter with a Russian interface, hiring for an English-speaking role.
        json={
            "text": "Backend engineer",
            "company_id": str(COMPANY_ID),
            "owner_uid": "bob",
            "language": "ru",
        },
        headers=headers(),
    )

    assert response.status_code == 201
    assert response.json()["language"] == "en"
    assert queue == [("bob", "interview", COMPANY_ID, "en")]


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


def test_a_chosen_language_wins_over_the_texts_own(client, queue):
    # A Russian job description, generated as a German kit.
    response = client.post(
        "/generations", json={"text": "Ищем Python-разработчика", "generate_in": "de"}
    )

    assert response.json()["language"] == "de"
    assert queue == [("ann", "preparation", None, "de")]


def test_a_recruiter_can_choose_the_interviews_language(client, queue):
    response = client.post(
        "/internal/generations",
        json={
            "text": "Backend engineer",
            "company_id": str(COMPANY_ID),
            "owner_uid": "bob",
            "generate_in": "ar",
        },
        headers=headers(),
    )

    assert response.json()["language"] == "ar"


def test_only_supported_languages_can_be_chosen(client, queue):
    response = client.post("/generations", json={"text": "Backend", "generate_in": "xx"})

    assert response.status_code == 422
    assert queue == []


def test_the_languages_to_generate_in_are_listed(client):
    languages = client.get("/languages").json()

    assert languages[0] == "en"
    assert languages == list(LANGUAGES)
