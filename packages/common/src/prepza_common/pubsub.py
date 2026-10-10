import asyncio
import base64
import json
import os
import uuid

from prepza_common import http
from prepza_common.constants import (
    EVENT_ID_ATTRIBUTE,
    EVENTS_TOPIC,
    HTTP_TIMEOUT_SECONDS,
    PUBSUB_URL,
)
from prepza_common.google import access_token, project, running_locally
from pydantic import BaseModel


def message(event_type: str, data: dict, event_id: str | None = None) -> dict:
    """One event as Pub/Sub takes it, with its own id: `event_id` when given (it stays the same on
    a re-send), otherwise a new one. Consumers never fall back on Pub/Sub's message id, which the
    local emulator numbers from 1 again after a restart, so a new event could look like one already
    handled and be dropped."""
    attributes = {"type": event_type, EVENT_ID_ATTRIBUTE: event_id or uuid.uuid4().hex}

    return {"data": base64.b64encode(json.dumps(data).encode()).decode(), "attributes": attributes}


async def publish_batch(messages: list[dict], timeout: float = HTTP_TIMEOUT_SECONDS) -> None:
    """Publishes events to the `events` topic in one call; Pub/Sub takes all or none. Each
    consumer gets them pushed to its /internal/events, and Pub/Sub retries until they're handled.
    Locally they go to the emulator."""
    headers = {}

    if running_locally():
        base = f"http://{os.environ['PUBSUB_EMULATOR_HOST']}"
    else:
        base = PUBSUB_URL
        headers["Authorization"] = f"Bearer {await asyncio.to_thread(access_token)}"

    response = await http.get_client().post(
        f"{base}/v1/projects/{project()}/topics/{EVENTS_TOPIC}:publish",
        json={"messages": messages},
        headers=headers,
        timeout=timeout,
    )

    response.raise_for_status()


async def publish(event_type: str, data: dict, timeout: float = HTTP_TIMEOUT_SECONDS) -> None:
    """Publishes one domain event (see publish_batch)."""
    await publish_batch([message(event_type, data)], timeout)


class PushMessage(BaseModel):
    data: str = ""
    attributes: dict[str, str] = {}
    messageId: str


class PushBody(BaseModel):
    """What Pub/Sub sends to a push endpoint."""

    message: PushMessage
    subscription: str


def event_of(body: PushBody) -> tuple[str, dict, str]:
    """The event's type, its data, and its id: the outbox's id, the same however often the event
    is re-sent, or else Pub/Sub's (the same across Pub/Sub's own retries)."""
    data = json.loads(base64.b64decode(body.message.data)) if body.message.data else {}
    attributes = body.message.attributes
    event_id = attributes.get(EVENT_ID_ATTRIBUTE) or body.message.messageId

    return attributes.get("type", ""), data, event_id
