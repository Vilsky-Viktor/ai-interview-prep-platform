import base64
import hashlib
import hmac
import json
import time

import pytest

from app.config.settings import settings
from app.helpers.emails import candidate_invite_email, share_invite_email
from app.helpers.webhooks import signature_valid
from app.integrations import companies, library

# Svix's published example (docs.svix.com, "Verifying Webhooks Manually").
SVIX_SECRET = "whsec_plJ3nmyCDGBKInavdOK15jsl"
SVIX_BODY = b'{"event_type":"ping","data":{"success":true}}'
SVIX_ID = "msg_loFOjxBNrRLzqYUf"
SVIX_TIMESTAMP = "1731705121"
SVIX_SIGNATURE = "v1,rAvfW3dJ/X/qxhsaXPOyyCGmRKsaKWcsNccKXlIktD0="

SECRET = "whsec_" + base64.b64encode(b"test-webhook-key").decode()
INVITE_ID = "6f1c2c1e-0000-4000-8000-000000000001"


def valid(signature=SVIX_SIGNATURE, now=int(SVIX_TIMESTAMP), secret=SVIX_SECRET):
    return signature_valid(SVIX_ID, SVIX_TIMESTAMP, signature, SVIX_BODY, secret, now, 300)


def test_svix_example_signature_is_accepted():
    assert valid()


def test_signature_list_with_other_versions_is_accepted():
    assert valid(f"v2,abc {SVIX_SIGNATURE}")


def test_wrong_signature_stale_timestamp_or_no_secret_is_refused():
    assert not valid("v1,rAvfW3dJ/X/qxhsaXPOyyCGmRKsaKWcsNccKXlIktD0x")
    assert not valid(now=int(SVIX_TIMESTAMP) + 301)
    assert not valid(secret="")


def signed_post(client, event: dict):
    """Posts the event as Resend would, signed with SECRET."""
    body = json.dumps(event).encode()
    timestamp = str(int(time.time()))
    key = base64.b64decode(SECRET.removeprefix("whsec_"))
    digest = hmac.new(key, f"msg_1.{timestamp}.".encode() + body, hashlib.sha256).digest()
    headers = {
        "svix-id": "msg_1",
        "svix-timestamp": timestamp,
        "svix-signature": "v1," + base64.b64encode(digest).decode(),
        "content-type": "application/json",
    }

    return client.post("/webhooks/resend", content=body, headers=headers)


@pytest.fixture
def reported(monkeypatch):
    """Records which owner was told about which invite."""
    calls = []

    async def fake_invite(invite_id):
        calls.append(("companies", invite_id))

    async def fake_share(share_id):
        calls.append(("library", share_id))

    monkeypatch.setattr(settings, "resend_webhook_secret", SECRET)
    monkeypatch.setattr(companies, "invite_undelivered", fake_invite)
    monkeypatch.setattr(library, "share_undelivered", fake_share)

    return calls


def event(event_type, kind=None):
    tags = {"kind": kind, "id": INVITE_ID} if kind else {}

    return {"type": event_type, "data": {"to": ["bob@example.com"], "tags": tags}}


def test_a_bounced_candidate_invite_is_reported_to_companies(client, reported):
    assert signed_post(client, event("email.bounced", "candidate_invite")).status_code == 204
    assert reported == [("companies", INVITE_ID)]


def test_a_spam_complaint_on_a_share_is_reported_to_library(client, reported):
    assert signed_post(client, event("email.complained", "share")).status_code == 204
    assert reported == [("library", INVITE_ID)]


def test_other_events_and_untagged_emails_are_ignored(client, reported):
    assert signed_post(client, event("email.delivered", "share")).status_code == 204
    assert signed_post(client, event("email.bounced")).status_code == 204
    assert reported == []


def test_an_unsigned_webhook_is_refused(client, reported):
    response = client.post("/webhooks/resend", json=event("email.bounced", "share"))

    assert response.status_code == 401
    assert reported == []


def test_invite_emails_are_tagged_with_what_they_are():
    base = {"email": "bob@example.com", "token": "t", "title": "Backend"}
    share = share_invite_email({**base, "inviter": "Ann", "share_id": INVITE_ID}, "http://x")
    invite = candidate_invite_email({**base, "company": "Acme", "invite_id": INVITE_ID}, "http://x")
    untagged = share_invite_email({**base, "inviter": "Ann"}, "http://x")

    assert share.tags == {"kind": "share", "id": INVITE_ID}
    assert invite.tags == {"kind": "candidate_invite", "id": INVITE_ID}
    assert untagged.tags == {}
