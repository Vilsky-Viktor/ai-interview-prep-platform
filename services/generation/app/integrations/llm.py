from functools import cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config.settings import settings
from app.constants.generation import LLM_TIMEOUT_SECONDS, MAX_OUTPUT_TOKENS
from app.constants.reuse import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from app.integrations.llm_limiter import SharedRateLimiter


# Reasoning models reject temperature unless reasoning_effort is "none".
@cache
def build_llm(model: str, reasoning_effort: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        reasoning_effort=reasoning_effort,
        max_retries=5,
        max_tokens=MAX_OUTPUT_TOKENS,
        timeout=LLM_TIMEOUT_SECONDS,
        rate_limiter=get_rate_limiter(),
    )


def get_generation_llm() -> ChatOpenAI:
    return build_llm(settings.generation_model, settings.generation_reasoning_effort)


def get_verifier_llm() -> ChatOpenAI:
    return build_llm(settings.verify_model, settings.verify_reasoning_effort)


def get_title_check_llm() -> ChatOpenAI:
    return build_llm(settings.title_check_model, settings.title_check_reasoning_effort)


@cache
def get_rate_limiter() -> SharedRateLimiter | None:
    if settings.llm_requests_per_second == 0:
        return None

    return SharedRateLimiter(settings.llm_requests_per_second)


@cache
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS, timeout=LLM_TIMEOUT_SECONDS
    )
