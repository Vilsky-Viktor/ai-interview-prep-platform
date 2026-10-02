import base64
import json

import pytest

from app.config.settings import settings
from app.helpers.emails import candidate_invite_email, share_invite_email
from app.integrations import resend, smtp

DATA = {"email": "bob@example.com", "token": "abc", "title": "Backend", "inviter": "Ann"}


def push(event_type="preparation.shared", data=DATA, message_id="m-1"):
    """A Pub/Sub push of one event, as the emulator sends it (no token)."""
    return {
        "message": {
            "data": base64.b64encode(json.dumps(data).encode()).decode(),
            "attributes": {"type": event_type},
            "messageId": message_id,
        },
        "subscription": "projects/demo-test/subscriptions/notifications-events",
    }


@pytest.fixture(autouse=True)
def emulator(monkeypatch):
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "pubsub:8085")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "demo-test")


def test_candidate_invite_email():
    data = {
        "email": "bob@example.com",
        "token": "xyz",
        "title": "Backend",
        "company": "Acme",
    }
    email = candidate_invite_email(data, "http://localhost:8090")

    assert email.to == "bob@example.com"
    assert email.subject == "Acme invited you to an interview"
    assert "http://localhost:8090/invite/xyz" in email.text
    assert 'href="http://localhost:8090/invite/xyz"' in email.html
    assert "Acme invited you to the “Backend” interview on prepza." in email.text
    assert ">Acme</strong> invited you" in email.html


def test_share_invite_email():
    email = share_invite_email(DATA, "http://localhost:8090/")

    assert email.to == "bob@example.com"
    assert email.subject == "Ann shared “Backend” with you"
    assert "http://localhost:8090/share/abc" in email.text
    assert ">Ann</strong> invited you to prepare with “Backend”" in email.html


def test_html_escapes_names_and_titles():
    email = share_invite_email({**DATA, "inviter": "<b>Ann</b>"}, "http://localhost:8090")

    assert "<b>Ann</b>" not in email.html
    assert "&lt;b&gt;Ann&lt;/b&gt;" in email.html
    assert "<b>Ann</b> invited you" in email.text


def test_a_share_event_sends_its_email(client, monkeypatch):
    sent = []

    async def fake_send(email):
        sent.append(email.to)

    monkeypatch.setattr(smtp, "send", fake_send)

    assert client.post("/internal/events", json=push()).status_code == 204
    assert sent == ["bob@example.com"]


def test_resend_gets_the_message_id_so_a_retry_never_sends_twice(client, monkeypatch):
    sent = []

    async def fake_send(email, idempotency_key):
        sent.append((email.to, idempotency_key))

    monkeypatch.setattr(settings, "resend_api_key", "re_test")
    monkeypatch.setattr(resend, "send", fake_send)

    client.post("/internal/events", json=push(message_id="m-7"))
    client.post("/internal/events", json=push(message_id="m-7"))

    assert sent == [("bob@example.com", "events/m-7")] * 2


def test_a_failed_send_answers_with_an_error_so_pubsub_retries(client, monkeypatch):
    async def failing_send(email):
        raise ConnectionError("SMTP is down")

    monkeypatch.setattr(smtp, "send", failing_send)

    with pytest.raises(ConnectionError):
        client.post("/internal/events", json=push())


def test_other_events_are_accepted_without_an_email(client):
    response = client.post("/internal/events", json=push("answer.recorded", {}))

    assert response.status_code == 204
