import asyncio
import base64
import json
import os

from prepza_common import http
from prepza_common.constants import EVENTS_TOPIC, PUBSUB_URL
from prepza_common.google import access_token, project, running_locally
from pydantic import BaseModel


async def publish(event_type: str, data: dict) -> None:
    """Publishes a domain event to the `events` topic; each consumer gets it pushed to its
    /internal/events, and Pub/Sub retries until it's handled. Locally it goes to the emulator."""
    headers = {}

    if running_locally():
        base = f"http://{os.environ['PUBSUB_EMULATOR_HOST']}"
    else:
        base = PUBSUB_URL
        headers["Authorization"] = f"Bearer {await asyncio.to_thread(access_token)}"

    message = {
        "data": base64.b64encode(json.dumps(data).encode()).decode(),
        "attributes": {"type": event_type},
    }
    response = await http.get_client().post(
        f"{base}/v1/projects/{project()}/topics/{EVENTS_TOPIC}:publish",
        json={"messages": [message]},
        headers=headers,
    )

    response.raise_for_status()


class PushMessage(BaseModel):
    data: str = ""
    attributes: dict[str, str] = {}
    messageId: str


class PushBody(BaseModel):
    """What Pub/Sub sends to a push endpoint."""

    message: PushMessage
    subscription: str


def event_of(body: PushBody) -> tuple[str, dict, str]:
    """The event's type, its data, and Pub/Sub's id for it (stable across retries)."""
    data = json.loads(base64.b64decode(body.message.data)) if body.message.data else {}

    return body.message.attributes.get("type", ""), data, body.message.messageId
