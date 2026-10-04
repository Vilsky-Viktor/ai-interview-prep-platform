import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.constants import CHAT_TURN_CREDITS
from prepza_common.i18n import translate
from prepza_common.rate_limit import hit

from app.config.settings import settings
from app.constants.rounds import CHAT_FAILED, NOT_ENOUGH_CREDITS
from app.helpers.chat import free_turns_left, user_turns
from app.helpers.sse import sse_event
from app.integrations import billing
from app.integrations.redis import get_redis
from app.schemas.chat import ChatMessageOut, ChatOut, ChatRequest
from app.services.access import get_owned_answer
from app.services.chat import build_messages, stream_reply
from app.storage import chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/answers", tags=["chat"])


async def charge_turn(user_id: str, key: str) -> None:
    """The reply is already given, so a failed charge is logged rather than taken back."""
    try:
        await billing.charge_chat_turn(user_id, key)
    except Exception:
        logger.exception("Couldn't charge chat turn %s", key)


@router.get("/{answer_id}/chat")
async def list_chat(answer_id: UUID, user: CurrentUser) -> ChatOut:
    await get_owned_answer(answer_id, user)
    history = await chat.list_messages(answer_id)

    return ChatOut(
        messages=[ChatMessageOut.model_validate(item) for item in history],
        free_turns_left=free_turns_left(history),
        turn_credits=CHAT_TURN_CREDITS,
    )


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
    paid = free_turns_left(history) == 0

    # Checked before the reply, charged after it: a reply that fails costs nothing.
    if paid and await billing.available_credits(user.uid) < CHAT_TURN_CREDITS:
        await track("balance_too_low", user_id=user.uid, what="chat")

        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH_CREDITS)

    messages = build_messages(round_, answer, history, body.message.strip(), user.language)

    async def events():
        reply = []

        try:
            async for delta in stream_reply(messages):
                reply.append(delta)
                yield sse_event({"delta": delta})
        except Exception:
            logger.exception("Chat failed for answer %s", answer_id)
            yield sse_event({"error": translate(CHAT_FAILED, user.language)})

            return

        await chat.add_exchange(answer_id, body.message.strip(), "".join(reply))

        if paid:
            await charge_turn(user.uid, f"{answer_id}:{user_turns(history) + 1}")

        await track("chat_turn", user_id=user.uid, paid=paid, turn=user_turns(history) + 1)

        yield sse_event({"done": True})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        # Tells nginx not to buffer the stream.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
