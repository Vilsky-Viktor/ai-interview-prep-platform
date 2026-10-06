from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES

from app.constants.faq import FAQS
from app.constants.help import HELP_HISTORY_CHARACTERS, HELP_HISTORY_MESSAGES, HelpRole
from app.constants.legal import COMPANY
from app.constants.privacy import PRIVACY_INTRO, PRIVACY_SECTIONS
from app.constants.terms import TERMS_INTRO, TERMS_SECTIONS
from app.helpers.help import faq_text, guide, legal_text, prices_text
from app.integrations import llm
from app.prompts.help import HELP_SYSTEM
from app.schemas.help import HelpMessage


def build_messages(
    conversation: list[HelpMessage], language: str, catalog: dict | None
) -> list[BaseMessage]:
    """The system prompt holds everything the chat may answer from, in English; it replies in
    the page's language."""
    system = HELP_SYSTEM.format(
        email=COMPANY["email"],
        guide=guide(),
        faq=faq_text(FAQS[DEFAULT_LANGUAGE], catalog),
        prices=prices_text(catalog),
        terms=legal_text(TERMS_INTRO, TERMS_SECTIONS),
        privacy=legal_text(PRIVACY_INTRO, PRIVACY_SECTIONS),
        language=LANGUAGES[language],
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
