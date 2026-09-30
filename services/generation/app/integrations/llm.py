from functools import cache

from langchain_openai import ChatOpenAI

from app.config.settings import settings


@cache
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.llm_model, temperature=0, max_retries=5)


@cache
def get_question_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.llm_model, temperature=0.5, max_retries=5)
