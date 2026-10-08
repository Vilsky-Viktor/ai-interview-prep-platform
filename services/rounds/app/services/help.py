from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from prepza_common import memory_cache
from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES
from prepza_common.scope import SCOPE_RULE

from app.constants.help import (
    GUIDE_CACHE_SECONDS,
    HELP_HISTORY_CHARACTERS,
    HELP_HISTORY_MESSAGES,
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
    question = conversation[-1]
    earlier = []
    room = HELP_HISTORY_CHARACTERS

    # The latest messages before the question, while they fit.
    for item in reversed(conversation[-(HELP_HISTORY_MESSAGES + 1) : -1]):
        room -= len(item.content)

        if room < 0:
            break

        earlier.insert(0, item)

    messages: list[BaseMessage] = [SystemMessage(content=system)]

    for item in [*earlier, question]:
        message_class = HumanMessage if item.role == HelpRole.USER else AIMessage
        messages.append(message_class(content=item.content))

    return messages


async def stream_reply(messages: list[BaseMessage]) -> AsyncIterator[str]:
    async for chunk in llm.get_help_llm().astream(messages):
        if chunk.content:
            yield chunk.content


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
