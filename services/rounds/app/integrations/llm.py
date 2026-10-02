from functools import cache

from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.constants.rounds import CHAT_TIMEOUT_SECONDS


# Reasoning models accept temperature only with reasoning_effort "none", which also keeps replies fast.
@cache
def get_chat_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        reasoning_effort="none",
        temperature=0.3,
        max_retries=3,
        timeout=CHAT_TIMEOUT_SECONDS,
    )
