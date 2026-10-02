from fastapi import APIRouter, status
from prepza_common.google import Invoker
from prepza_common.pubsub import PushBody, event_of

from app.services.events import handle

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/events", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Invoker])
async def receive_event(body: PushBody) -> None:
    """Pub/Sub pushes every event here. A failed email answers with an error, so Pub/Sub
    retries it, and moves it to the dead-letter topic after the subscription's maximum
    attempts; Resend never sends the same message twice."""
    event_type, data, message_id = event_of(body)
    await handle(event_type, data, message_id)
