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


# Reasoning models accept temperature only with reasoning_effort "none", which also keeps replies fast.
@cache
def get_help_llm() -> ChatOpenAI:
    """The FAQ's help chat."""
    return ChatOpenAI(
        model=settings.llm_model,
        reasoning_effort="none",
        temperature=0.3,
        max_retries=3,
        timeout=CHAT_TIMEOUT_SECONDS,
    )
