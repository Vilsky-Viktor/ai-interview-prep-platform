from functools import cache

from langchain_openai import ChatOpenAI
from prepza_common.llm import chat_model

from app.config.settings import settings
from app.constants.rounds import CHAT_TIMEOUT_SECONDS


@cache
def get_help_llm() -> ChatOpenAI:
    """The FAQ's help chat; at effort "none" it answers at a low temperature."""
    return chat_model(
        settings.help_model,
        settings.help_reasoning_effort,
        temperature=0.3,
        max_retries=3,
        timeout=CHAT_TIMEOUT_SECONDS,
    )
