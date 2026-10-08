from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from prepza_common.i18n import request_language
from prepza_common.sse import event_stream

from app.auth import UserWithToken
from app.constants.chat import MAX_MESSAGE_LENGTH
from app.constants.limits import MAX_AUDIO_SECONDS, MESSAGES_PER_USER_DAY, MESSAGES_PER_USER_HOUR
from app.schemas.chat import ChatRequest, ConfigOut
from app.services import turns

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(body: ChatRequest, request: Request, auth: UserWithToken) -> StreamingResponse:
    """A message to the assistant, which answers from the services' data the user may read, in
    the interface's language. Server-sent events: {"conversation": {"id"}}, then any of
    {"tool": {"name", "state", "label"}}, {"block"} and {"delta"}, and last {"done":
    {"message_id"}} or {"error"} ({"code": "session_expired"} when the user's token stopped
    working: refresh it and send again); a keep-alive comment every 15 s. Refused before it
    streams during the emergency pause and over a limit."""
    user, token = auth
    events = await turns.start(body, user, token, request_language(request))

    return event_stream(events)


@router.get("/config")
async def config(auth: UserWithToken) -> ConfigOut:
    """The limits the panel keeps to."""
    return ConfigOut(
        max_message_length=MAX_MESSAGE_LENGTH,
        max_audio_seconds=MAX_AUDIO_SECONDS,
        messages_per_hour=MESSAGES_PER_USER_HOUR,
        messages_per_day=MESSAGES_PER_USER_DAY,
    )
