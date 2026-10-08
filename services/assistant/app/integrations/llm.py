from functools import cache

from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI
from prepza_common.llm import chat_model

from app.config.settings import settings
from app.constants.chat import MAX_ANSWER_TOKENS, MODEL_RETRIES, MODEL_TIMEOUT_SECONDS
from app.constants.titles import TITLE_MAX_TOKENS, TITLE_REASONING_EFFORT
from app.constants.transcribe import TRANSCRIBE_RETRIES, TRANSCRIBE_TIMEOUT_SECONDS


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


@cache
def get_openai() -> AsyncOpenAI:
    """OpenAI's own client, for speech to text."""
    return AsyncOpenAI(
        api_key=settings.openai_api_key or None,
        timeout=TRANSCRIBE_TIMEOUT_SECONDS,
        max_retries=TRANSCRIBE_RETRIES,
    )


@cache
def get_title_model() -> ChatOpenAI:
    """The conversations' titles: the assistant's model, without reasoning, a few tokens."""
    return chat_model(
        settings.assistant_model,
        TITLE_REASONING_EFFORT,
        max_tokens=TITLE_MAX_TOKENS,
        timeout=MODEL_TIMEOUT_SECONDS,
        max_retries=MODEL_RETRIES,
    )
