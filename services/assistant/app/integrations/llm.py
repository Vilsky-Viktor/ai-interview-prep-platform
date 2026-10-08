from functools import cache

from langchain_openai import ChatOpenAI
from prepza_common.llm import chat_model

from app.config.settings import settings
from app.constants.chat import MAX_ANSWER_TOKENS, MODEL_RETRIES, MODEL_TIMEOUT_SECONDS


@cache
def get_chat_model() -> ChatOpenAI:
    """The assistant's model; it reports each call's tokens as it streams."""
    return chat_model(
        settings.assistant_model,
        settings.assistant_reasoning_effort,
        stream_usage=True,
        max_tokens=MAX_ANSWER_TOKENS,
        timeout=MODEL_TIMEOUT_SECONDS,
        max_retries=MODEL_RETRIES,
    )
