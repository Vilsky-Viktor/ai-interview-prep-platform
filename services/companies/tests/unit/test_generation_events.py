import base64
import json
import uuid
from types import SimpleNamespace

import pytest
from prepza_common.notifications import notification

from app.services import outbox as outbox_service
from app.storage import interviews

GENERATION_ID = uuid.uuid4()
SET_ID = uuid.uuid4()
INTERVIEW = SimpleNamespace(id=uuid.uuid4(), company_id=uuid.uuid4(), title=None)


def push(event_type, data):
    """A Pub/Sub push of one event, as the emulator sends it (no token)."""
    return {
        "message": {
            "data": base64.b64encode(json.dumps(data).encode()).decode(),
            "attributes": {"type": event_type},
            "messageId": "1",
        },
        "subscription": "projects/demo-test/subscriptions/companies-events",
    }


COMPLETED = {
    "generation_id": str(GENERATION_ID),
    "company_id": str(uuid.uuid4()),
    "set_id": str(SET_ID),
    "title": "Bookkeeper interview",
}


@pytest.fixture(autouse=True)
def emulator(monkeypatch):
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "pubsub:8085")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-test")


@pytest.fixture(autouse=True)
def interview(monkeypatch):
    async def found(generation_id):
        return INTERVIEW

    async def no_flush():
        pass

    monkeypatch.setattr(interviews, "get_for_generation", found)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)


def test_finished_generation_is_stored_on_its_interview_and_the_company_told(client, monkeypatch):
    stored = []

    async def set_generated(generation_id, set_id, title, notice):
        stored.append((generation_id, set_id, title, notice))

    monkeypatch.setattr(interviews, "set_generated", set_generated)

    response = client.post("/internal/events", json=push("generation.completed", COMPLETED))

    company = INTERVIEW.company_id
    ready = notification(
        "company",
        company,
        "interview_ready",
        f"/company/{company}/interviews/{INTERVIEW.id}",
        key=str(INTERVIEW.id),
        title="Bookkeeper interview",
    )
    assert response.status_code == 204
    assert stored == [(GENERATION_ID, SET_ID, "Bookkeeper interview", ready)]


def test_a_cancelled_generation_removes_its_interview_and_tells_the_company(client, monkeypatch):
    removed = []

    async def remove_for_generation(generation_id, notice):
        removed.append((generation_id, notice))

    monkeypatch.setattr(interviews, "remove_for_generation", remove_for_generation)
    event = push("generation.cancelled", {"generation_id": str(GENERATION_ID)})

    company = INTERVIEW.company_id
    cancelled = notification(
        "company", company, "interview_cancelled", f"/company/{company}/interviews"
    )
    assert client.post("/internal/events", json=event).status_code == 204
    assert removed == [(GENERATION_ID, cancelled)]


def test_an_interview_already_removed_is_left_alone(client, monkeypatch):
    async def gone(generation_id):
        return None

    monkeypatch.setattr(interviews, "get_for_generation", gone)

    response = client.post("/internal/events", json=push("generation.completed", COMPLETED))

    assert response.status_code == 204


def test_other_events_are_accepted_without_action(client):
    assert client.post("/internal/events", json=push("candidate.invited", {})).status_code == 204


def test_a_failure_answers_with_an_error_so_pubsub_retries(client, monkeypatch):
    async def database_down(*args):
        raise ConnectionError("database is down")

    monkeypatch.setattr(interviews, "set_generated", database_down)

    with pytest.raises(ConnectionError):
        client.post("/internal/events", json=push("generation.completed", COMPLETED))
