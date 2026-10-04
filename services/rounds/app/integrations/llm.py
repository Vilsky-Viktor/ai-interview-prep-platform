from functools import cache

from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.constants.rounds import CHAT_TIMEOUT_SECONDS


@cache
def get_tutor_llm() -> ChatOpenAI:
    """The tutor that explains a question; it reasons, so it takes no temperature."""
    return ChatOpenAI(
        model=settings.tutor_model,
        reasoning_effort=settings.tutor_reasoning_effort,
        max_retries=3,
        timeout=CHAT_TIMEOUT_SECONDS,
    )


@cache
def get_help_llm() -> ChatOpenAI:
    """The FAQ's help chat. Reasoning models accept a temperature only at effort "none"."""
    effort = settings.help_reasoning_effort

    return ChatOpenAI(
        model=settings.help_model,
        reasoning_effort=effort,
        temperature=0.3 if effort == "none" else None,
        max_retries=3,
        timeout=CHAT_TIMEOUT_SECONDS,
    )
