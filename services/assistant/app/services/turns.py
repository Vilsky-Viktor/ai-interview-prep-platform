import asyncio
import logging
from collections.abc import AsyncIterator

import anyio
from prepza_common.i18n import translate
from prepza_common.pause import refuse_if_paused
from prepza_common.sse import KEEP_ALIVE, sse_event
from prepza_common.user import User

from app.constants.chat import (
    CHAT_FAILED,
    HISTORY_CHARACTERS,
    HISTORY_MESSAGES,
    KEEP_ALIVE_SECONDS,
    SESSION_EXPIRED,
    SESSION_EXPIRED_CODE,
    TITLE_LENGTH,
    TURN_SECONDS,
    Status,
)
from app.integrations.redis import get_redis
from app.models.answers import Answer, Turn
from app.schemas.chat import ChatRequest
from app.services import limits
from app.services.chat import Emit, SessionExpired, build_messages, converse
from app.services.conversations import open_conversation, require_company
from app.storage import conversations, messages

logger = logging.getLogger(__name__)

# What the turn puts last on its queue: nothing more comes.
END = object()


async def start(body: ChatRequest, user: User, token: str, language: str) -> AsyncIterator[str]:
    """Checks a new message before anything streams (plain HTTP errors): the pause, the
    conversation (the user's own, about a company they can still see), the limits. Then saves it
    and returns the turn's events."""
    redis = get_redis()
    await refuse_if_paused(redis)
    conversation = None
    company_id = body.company_id

    if body.conversation_id is not None:
        conversation = await open_conversation(body.conversation_id, user.uid, token, language)
        company_id = conversation.company_id
    elif company_id is not None:
        await require_company(company_id, token, language)

    await limits.check(redis, user.uid, company_id)

    if conversation is None:
        conversation = await conversations.create(user.uid, company_id, body.message[:TITLE_LENGTH])

    earlier = await messages.recent(conversation.id, HISTORY_MESSAGES)
    await messages.add_question(conversation.id, body.message, body.source)
    turn = Turn(conversation.id, user.uid, company_id, token, language)

    return stream(turn, build_messages(turn, earlier, body.message, body.page, HISTORY_CHARACTERS))


async def stream(turn: Turn, prompt: list) -> AsyncIterator[str]:
    """The turn's events: the conversation's id first, a keep-alive comment whenever nothing
    came for KEEP_ALIVE_SECONDS. The turn runs as a task of its own; when the client goes (the
    user stopped it, or closed the tab), it's cancelled and saves what it had."""
    queue: asyncio.Queue = asyncio.Queue()
    task = asyncio.create_task(run_turn(turn, prompt, queue.put_nowait))

    try:
        yield sse_event({"conversation": {"id": str(turn.conversation_id)}})

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), KEEP_ALIVE_SECONDS)
            except TimeoutError:
                yield KEEP_ALIVE

                continue

            if event is END:
                return

            yield sse_event(event)
    finally:
        task.cancel()

        # The request may be cancelled itself: waiting for the turn to save must not be.
        with anyio.CancelScope(shield=True):
            await asyncio.wait({task})


async def run_turn(turn: Turn, prompt: list, emit: Emit) -> None:
    """Runs the conversation loop within TURN_SECONDS and saves the answer however it ends:
    complete, cancelled (with its text so far) or failed. Its tokens count against the budgets.
    Ends with {"done": {"message_id"}} or a translated {"error"}, then END."""
    answer = Answer()
    status = Status.COMPLETE
    error = None

    try:
        async with asyncio.timeout(TURN_SECONDS):
            await converse(prompt, turn, answer, emit)
    except asyncio.CancelledError:
        # Nobody reads the events any more; the answer is still saved below.
        asyncio.current_task().uncancel()
        status = Status.CANCELLED
    except SessionExpired:
        status = Status.FAILED
        error = {"error": translate(SESSION_EXPIRED, turn.language), "code": SESSION_EXPIRED_CODE}
    except Exception:
        # The model failed, or the turn ran out of time.
        logger.exception("An assistant turn failed")
        status = Status.FAILED
        error = {"error": translate(CHAT_FAILED, turn.language)}

    await limits.record(get_redis(), turn.user_id, turn.company_id, answer.tokens)
    last = error or {"error": translate(CHAT_FAILED, turn.language)}

    try:
        message_id = await messages.add_answer(turn.conversation_id, answer, status)

        if error is None:
            last = {"done": {"message_id": str(message_id)}}
    except Exception:
        # The conversation was deleted meanwhile (its company, or by the user).
        logger.exception("Couldn't save an assistant answer")
    finally:
        # However the turn ended, the panel hears how, and the stream ends.
        emit(last)
        emit(END)
