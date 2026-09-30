import logging
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.auth import CurrentUser
from app.config.settings import settings
from app.constants.rounds import CHAT_FAILED
from app.helpers.rate_limit import hit
from app.helpers.sse import sse_event
from app.integrations.redis import get_redis
from app.schemas.chat import ChatMessageOut, ChatRequest
from app.services.access import get_owned_answer
from app.services.chat import build_messages, stream_reply
from app.storage import chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/answers", tags=["chat"])


@router.get("/{answer_id}/chat")
async def list_chat(answer_id: UUID, user: CurrentUser) -> list[ChatMessageOut]:
    await get_owned_answer(answer_id, user)

    return [ChatMessageOut.model_validate(item) for item in await chat.list_messages(answer_id)]


@router.post("/{answer_id}/chat")
async def send_chat(answer_id: UUID, body: ChatRequest, user: CurrentUser) -> StreamingResponse:
    """Streams the reply as server-sent events: {"delta"}..., then {"done"} or {"error"}."""
    answer, round_ = await get_owned_answer(answer_id, user)

    await hit(
        get_redis(),
        f"rate:llm:{user.uid}",
        settings.llm_limit,
        settings.llm_window_seconds,
    )
    history = await chat.list_messages(answer_id)
    messages = build_messages(round_, answer, history, body.message.strip())

    async def events():
        reply = []

        try:
            async for delta in stream_reply(messages):
                reply.append(delta)
                yield sse_event({"delta": delta})
        except Exception:
            logger.exception("Chat failed for answer %s", answer_id)
            yield sse_event({"error": CHAT_FAILED})

            return

        await chat.add_exchange(answer_id, body.message.strip(), "".join(reply))
        yield sse_event({"done": True})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        # Tells nginx not to buffer the stream.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
