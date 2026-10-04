from functools import cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config.settings import settings
from app.constants.generation import LLM_TIMEOUT_SECONDS, MAX_OUTPUT_TOKENS
from app.constants.reuse import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from app.integrations.llm_limiter import SharedRateLimiter


# Reasoning models reject temperature unless reasoning_effort is "none".
@cache
def get_llm(reasoning_effort: str | None = None) -> ChatOpenAI:
    """Generation's model, at LLM_REASONING_EFFORT unless told otherwise."""
    return ChatOpenAI(
        model=settings.llm_model,
        reasoning_effort=reasoning_effort or settings.llm_reasoning_effort,
        max_retries=5,
        max_tokens=MAX_OUTPUT_TOKENS,
        timeout=LLM_TIMEOUT_SECONDS,
        rate_limiter=get_rate_limiter(),
    )


@cache
def get_rate_limiter() -> SharedRateLimiter | None:
    if settings.llm_requests_per_second == 0:
        return None

    return SharedRateLimiter(settings.llm_requests_per_second)


def get_verifier_llm() -> ChatOpenAI:
    return get_llm(settings.verify_reasoning_effort)


@cache
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS, timeout=LLM_TIMEOUT_SECONDS
    )
