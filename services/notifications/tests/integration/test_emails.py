import base64
import json

import httpx
import pytest
from prepza_common import http

from app.config.settings import settings
from tests.integration.factories import api, push, signed

SECRET = "whsec_" + base64.b64encode(b"test-webhook-key").decode()
INVITE_ID = "6f1c2c1e-0000-4000-8000-000000000001"
INVITE = {
    "email": "bob@example.com",
    "token": "t",
    "title": "Backend",
    "company": "Acme",
    "invite_id": INVITE_ID,
}
PDF = base64.b64encode(b"%PDF-1.3 a report").decode()
REPORT = {
    "email": "boss@example.com",
    "sender": "Bob",
    "reply_to": "bob@example.com",
    "company": "Acme",
    "title": "Backend",
    "candidate": "ann@example.com",
    "language": "en",
    "filename": "Report.pdf",
    "pdf": PDF,
}


@pytest.fixture
def outside(monkeypatch):
    """Resend and the companies service at the HTTP boundary: every request is recorded, and
    Resend answers with `outside["resend"]`."""
    calls = {"requests": [], "resend": 200}

    def answer(request: httpx.Request) -> httpx.Response:
        calls["requests"].append(request)

        if request.url.host == "api.resend.com":
            return httpx.Response(calls["resend"], json={"id": "e-1"})

        return httpx.Response(204)

    monkeypatch.setattr(settings, "resend_api_key", "re_test")
    monkeypatch.setattr(settings, "resend_webhook_secret", SECRET)
    monkeypatch.setattr(settings, "companies_url", "http://companies")
    monkeypatch.setattr(
        http, "get_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(answer))
    )

    return calls


def post_events(run, *pushes) -> list[int]:
    async def scenario():
        async with api() as client:
            return [
                (await client.post("/internal/events", json=body)).status_code for body in pushes
            ]

    return run(scenario())


def test_a_shared_report_goes_through_resend_keyed_by_its_event(run, outside):
    codes = post_events(run, push("report.shared", REPORT, outbox_id="outbox-7"))
    [request] = outside["requests"]
    sent = json.loads(request.content)

    assert codes == [204]
    # The same key on every delivery of the event, so Resend sends it once.
    assert request.headers["Idempotency-Key"] == "events/outbox-7"
    assert sent["to"] == ["boss@example.com"]
    assert sent["reply_to"] == "bob@example.com"
    assert sent["attachments"] == [{"filename": "Report.pdf", "content": PDF}]


def test_a_contact_message_goes_to_the_inbox_and_replies_to_the_visitor(run, outside):
    message = {"name": "Eve", "email": "eve@example.com", "language": "en", "message": "Hi"}
    post_events(run, push("contact.sent", message, message_id="pubsub-9"))
    [request] = outside["requests"]
    sent = json.loads(request.content)

    # Without an outbox id, Pub/Sub's message id is the key.
    assert request.headers["Idempotency-Key"] == "events/pubsub-9"
    assert (sent["to"], sent["reply_to"]) == ([settings.contact_email], "eve@example.com")


def test_a_failing_resend_answers_with_an_error_so_pub_sub_retries(run, outside):
    outside["resend"] = 503

    assert post_events(run, push("report.shared", REPORT)) == [500]


def test_an_invite_resend_refuses_is_marked_undelivered_and_not_retried(run, outside):
    outside["resend"] = 422

    assert post_events(run, push("candidate.invited", INVITE)) == [204]
    assert [str(request.url) for request in outside["requests"][1:]] == [
        f"http://companies/internal/invites/{INVITE_ID}/undelivered"
    ]


def bounce() -> bytes:
    tags = {"kind": "candidate_invite", "id": INVITE_ID}

    return json.dumps({"type": "email.bounced", "data": {"tags": tags}}).encode()


def test_a_signed_bounce_marks_the_invite_undelivered(run, outside):
    async def scenario():
        async with api() as client:
            return await client.post(
                "/webhooks/resend", content=bounce(), headers=signed(bounce(), SECRET)
            )

    response = run(scenario())
    [request] = outside["requests"]

    assert response.status_code == 204
    assert str(request.url) == f"http://companies/internal/invites/{INVITE_ID}/undelivered"
    assert request.headers["Authorization"].startswith("Bearer ")


def test_a_webhook_with_a_wrong_signature_is_refused(run, outside):
    async def scenario():
        async with api() as client:
            headers = signed(bounce(), "whsec_" + base64.b64encode(b"another-key").decode())

            return await client.post("/webhooks/resend", content=bounce(), headers=headers)

    assert run(scenario()).status_code == 401
    assert outside["requests"] == []
