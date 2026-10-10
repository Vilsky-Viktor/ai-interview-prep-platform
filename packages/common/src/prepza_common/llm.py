"""OpenAI chat models, built one way by every service that talks to one. Needs the package's `llm`
extra (langchain-openai); the key comes from OPENAI_API_KEY."""

from langchain_openai import ChatOpenAI


def chat_model(
    model: str, reasoning_effort: str, temperature: float | None = None, **options
) -> ChatOpenAI:
    """A chat model thinking at `reasoning_effort` ("none", "minimal", "low", "medium", "high").

    Reasoning models accept a temperature only at effort "none", so at any other effort
    `temperature` is left out. `options` go to ChatOpenAI as they are (timeout, max_retries, ...).
    Nothing is stored at OpenAI: its Responses API, which a model with tools may use, would keep
    each call (and the people's data in it) by default.
    """
    return ChatOpenAI(
        model=model,
        reasoning_effort=reasoning_effort,
        temperature=temperature if reasoning_effort == "none" else None,
        store=False,
        **options,
    )
