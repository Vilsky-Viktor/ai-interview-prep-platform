from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES

from app.constants.certificate_rules import CERTIFICATE_RULES
from app.constants.faq import FAQS
from app.constants.help import HELP_HISTORY_MESSAGES, HelpRole
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
        certificate_rules="\n".join(CERTIFICATE_RULES[DEFAULT_LANGUAGE]),
        terms=legal_text(TERMS_INTRO, TERMS_SECTIONS),
        privacy=legal_text(PRIVACY_INTRO, PRIVACY_SECTIONS),
        language=LANGUAGES[language],
    )
    messages: list[BaseMessage] = [SystemMessage(content=system)]

    # The question, and the latest messages before it.
    for item in conversation[-(HELP_HISTORY_MESSAGES + 1) :]:
        message_class = HumanMessage if item.role == HelpRole.USER else AIMessage
        messages.append(message_class(content=item.content))

    return messages


async def stream_reply(messages: list[BaseMessage]) -> AsyncIterator[str]:
    async for chunk in llm.get_chat_llm().astream(messages):
        if chunk.content:
            yield chunk.content
