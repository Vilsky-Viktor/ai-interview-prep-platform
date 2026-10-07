import base64
import hashlib
import hmac
import json
import time
import uuid

import httpx
from prepza_common.constants import EVENT_ID_ATTRIBUTE
from prepza_common.notifications import NotificationKind, Recipient, notification

from app.main import app


def company() -> str:
    """A company of its own for each test: the database is shared by the whole run."""
    return f"c-{uuid.uuid4()}"


def finished(company_id: str, title: str = "Backend", **data) -> dict:
    """A "candidate finished" notification for the company, about its test `title`."""
    return notification(
        Recipient.COMPANY,
        company_id,
        NotificationKind.CANDIDATE_FINISHED,
        f"/companies/{company_id}",
        title=title,
        **data,
    )


def push(event_type: str, data: dict, outbox_id: str | None = None, message_id: str = "m-1"):
    """A Pub/Sub push of one event; an outbox event carries its own id as an attribute."""
    attributes = {"type": event_type, **({EVENT_ID_ATTRIBUTE: outbox_id} if outbox_id else {})}

    return {
        "message": {
            "data": base64.b64encode(json.dumps(data).encode()).decode(),
            "attributes": attributes,
            "messageId": message_id,
        },
        "subscription": "projects/demo-test/subscriptions/notifications-events",
    }


def api() -> httpx.AsyncClient:
    """The app itself, called in the test's own event loop; a failing route answers 500."""
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    return httpx.AsyncClient(transport=transport, base_url="http://notifications")


def signed(body: bytes, secret: str) -> dict:
    """Headers of a webhook signed as Resend (Svix) signs it with the `whsec_` secret."""
    timestamp = str(int(time.time()))
    key = base64.b64decode(secret.removeprefix("whsec_"))
    digest = hmac.new(key, f"msg_1.{timestamp}.".encode() + body, hashlib.sha256).digest()

    return {
        "svix-id": "msg_1",
        "svix-timestamp": timestamp,
        "svix-signature": "v1," + base64.b64encode(digest).decode(),
        "content-type": "application/json",
    }
