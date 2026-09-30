from functools import cache

from langchain_openai import ChatOpenAI

from app.config.settings import settings


@cache
def get_grader_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.llm_model, temperature=0, max_retries=3)


@cache
def get_chat_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.llm_model, temperature=0.3, max_retries=3)
