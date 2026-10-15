from collections.abc import AsyncIterator

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from prepza_common import memory_cache
from prepza_common.constants import DAY_SECONDS, DEFAULT_LANGUAGE, LANGUAGES
from prepza_common.llm import latest_messages
from prepza_common.rate_limit import add_spent
from prepza_common.scope import SCOPE_RULE

from app.constants.help import (
    GUIDE_CACHE_SECONDS,
    HELP_HISTORY_CHARACTERS,
    HELP_HISTORY_MESSAGES,
    HELP_SPEND_KEY,
    HELP_TOKENS_PER_DAY,
    HelpRole,
)
from app.constants.legal import COMPANY
from app.helpers.help import knowledge
from app.integrations import billing, llm
from app.prompts.help import HELP_SYSTEM
from app.schemas.help import HelpMessage


def build_messages(
    conversation: list[HelpMessage], language: str, catalog: dict | None
) -> list[BaseMessage]:
    """The system prompt holds everything the chat may answer from, in English; it replies in
    the page's language."""
    system = HELP_SYSTEM.format(
        email=COMPANY["email"],
        knowledge=knowledge(DEFAULT_LANGUAGE, catalog),
        language=LANGUAGES[language],
        scope=SCOPE_RULE,
    )
    # The latest messages before the question (the last one, the user's), while they fit.
    before = conversation[-(HELP_HISTORY_MESSAGES + 1) : -1]
    earlier = latest_messages(
        [(item.role == HelpRole.USER, item.content) for item in before], HELP_HISTORY_CHARACTERS
    )

    return [SystemMessage(content=system), *earlier, HumanMessage(content=conversation[-1].content)]


async def stream_reply(messages: list[BaseMessage], used: dict) -> AsyncIterator[str]:
    """The answer's text as it comes; its tokens (input and output) are added to `used`."""
    async for chunk in llm.get_help_llm().astream(messages):
        if chunk.usage_metadata:
            used["tokens"] = used.get("tokens", 0) + chunk.usage_metadata.get("total_tokens", 0)

        if chunk.content:
            yield chunk.content


async def record_spend(redis, tokens: int) -> None:
    """Adds an answer's tokens to the day's budget. Going over refuses the next question, not
    this one; with Redis down, the spending is lost rather than the answer."""
    await add_spent(redis, HELP_SPEND_KEY, tokens, HELP_TOKENS_PER_DAY, DAY_SECONDS)


async def platform_guide(language: str) -> str:
    """The help chat's knowledge with the FAQ in `language`, kept a while in this process."""
    key = f"help:guide:{language}"
    found = memory_cache.get(key)

    if found is None:
        catalog = await billing.catalog()
        found = knowledge(language, catalog)

        # Without billing's prices, it's made again next time.
        if catalog is not None:
            memory_cache.put(key, found, GUIDE_CACHE_SECONDS)

    return found
