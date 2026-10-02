import base64
import json
import uuid

import pytest

from app.storage import quality

QUESTION_ID = uuid.uuid4()


def push(event_type, data):
    """A Pub/Sub push of one event, as the emulator sends it (no token)."""
    return {
        "message": {
            "data": base64.b64encode(json.dumps(data).encode()).decode(),
            "attributes": {"type": event_type},
            "messageId": "1",
        },
        "subscription": "projects/demo-test/subscriptions/library-events",
    }


RECORDED = {
    "question_id": str(QUESTION_ID),
    "question_text": "Which account is debited?",
    "option": "Cash",
    "correct": True,
}


@pytest.fixture(autouse=True)
def emulator(monkeypatch):
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "pubsub:8085")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-test")


def test_recorded_answer_goes_into_the_question_statistics(client, monkeypatch):
    stored = []

    async def record_answer(question_id, question_text, option, correct):
        stored.append((question_id, question_text, option, correct))

    monkeypatch.setattr(quality, "record_answer", record_answer)

    response = client.post("/internal/events", json=push("answer.recorded", RECORDED))

    assert response.status_code == 204
    assert stored == [(QUESTION_ID, "Which account is debited?", "Cash", True)]


def test_other_events_are_accepted_without_action(client):
    response = client.post("/internal/events", json=push("preparation.shared", {}))

    assert response.status_code == 204


def test_a_failure_answers_with_an_error_so_pubsub_retries(client, monkeypatch):
    async def database_down(*args):
        raise ConnectionError("database is down")

    monkeypatch.setattr(quality, "record_answer", database_down)

    with pytest.raises(ConnectionError):
        client.post("/internal/events", json=push("answer.recorded", RECORDED))


def test_pushes_without_a_google_token_are_refused_in_google_cloud(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "prepza-prod")
    monkeypatch.setenv("INVOKER_AUDIENCE", "https://library.example.run.app")

    response = client.post("/internal/events", json=push("answer.recorded", RECORDED))

    assert response.status_code == 401
