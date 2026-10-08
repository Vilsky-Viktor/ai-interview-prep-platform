import logging

from langchain_core.messages import HumanMessage, SystemMessage
from prepza_common.constants import LANGUAGES

from app.constants.titles import MAX_TITLE_LENGTH, TITLE_SOURCE_CHARACTERS
from app.helpers.history import history
from app.helpers.titles import clean_title, should_title
from app.integrations import llm
from app.integrations.redis import get_redis
from app.models.answers import Turn
from app.prompts.titles import TITLE_SYSTEM
from app.services import limits
from app.storage import conversations, messages

logger = logging.getLogger(__name__)


async def refresh(turn: Turn) -> str | None:
    """A new title for the conversation when it's time (should_title), written by the cheap
    model call; its tokens count against the budgets. None when it isn't time or the call
    failed, and the old title stays."""
    if not should_title(await messages.count_questions(turn.conversation_id)):
        return None

    earlier = await messages.recent(turn.conversation_id, 20)
    chat = "\n".join(
        f"{message.type}: {message.content}"
        for message in history(earlier, TITLE_SOURCE_CHARACTERS)
    )
    system = TITLE_SYSTEM.format(length=MAX_TITLE_LENGTH, language=LANGUAGES[turn.language])

    try:
        reply = await llm.get_title_model().ainvoke(
            [SystemMessage(content=system), HumanMessage(content=chat)]
        )
    except Exception as failure:  # noqa: BLE001 - logged by its type only
        logger.error("A conversation's title failed: %s", type(failure).__name__)

        return None

    usage = reply.usage_metadata or {}
    tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    await limits.record(get_redis(), turn.user_id, turn.company_id, tokens)
    title = clean_title(reply.text)

    if title:
        await conversations.set_title(turn.conversation_id, title)

    return title
