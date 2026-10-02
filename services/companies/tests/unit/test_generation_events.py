import base64
import json
import uuid

import pytest

from app.storage import interviews

GENERATION_ID = uuid.uuid4()
SET_ID = uuid.uuid4()


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


def test_finished_generation_is_stored_on_its_interview(client, monkeypatch):
    stored = []

    async def set_generated(generation_id, set_id, title):
        stored.append((generation_id, set_id, title))

    monkeypatch.setattr(interviews, "set_generated", set_generated)

    response = client.post("/internal/events", json=push("generation.completed", COMPLETED))

    assert response.status_code == 204
    assert stored == [(GENERATION_ID, SET_ID, "Bookkeeper interview")]


def test_a_cancelled_generation_removes_its_interview(client, monkeypatch):
    removed = []

    async def remove_for_generation(generation_id):
        removed.append(generation_id)

    monkeypatch.setattr(interviews, "remove_for_generation", remove_for_generation)
    event = push("generation.cancelled", {"generation_id": str(GENERATION_ID)})

    assert client.post("/internal/events", json=event).status_code == 204
    assert removed == [GENERATION_ID]


def test_other_events_are_accepted_without_action(client):
    assert client.post("/internal/events", json=push("candidate.invited", {})).status_code == 204


def test_a_failure_answers_with_an_error_so_pubsub_retries(client, monkeypatch):
    async def database_down(*args):
        raise ConnectionError("database is down")

    monkeypatch.setattr(interviews, "set_generated", database_down)

    with pytest.raises(ConnectionError):
        client.post("/internal/events", json=push("generation.completed", COMPLETED))
