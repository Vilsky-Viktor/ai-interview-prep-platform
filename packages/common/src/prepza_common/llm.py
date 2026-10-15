"""OpenAI chat models, built one way by every service that talks to one. Needs the package's `llm`
extra (langchain-openai); the key comes from OPENAI_API_KEY."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from prepza_common.constants import MODEL_PRICES


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


def call_cost(model_name: str, usage: dict) -> float | None:
    """USD for a model's usage metadata, as LangChain reports it (cached input counted at the
    full price); None for a model without a price in MODEL_PRICES."""
    price = MODEL_PRICES.get(model_name)

    if price is None:
        return None

    return (
        usage.get("input_tokens", 0) * price[0] + usage.get("output_tokens", 0) * price[1]
    ) / 1e6


def latest_messages(messages: list[tuple[bool, str]], room: int) -> list[BaseMessage]:
    """What a model reads of a conversation: its latest messages (oldest first) within `room`
    characters. `messages` are (from the user, text), oldest first; one without text is left
    out."""
    kept: list[BaseMessage] = []

    for from_user, text in reversed(messages):
        if not text:
            continue

        room -= len(text)

        if room < 0:
            break

        kind = HumanMessage if from_user else AIMessage
        kept.insert(0, kind(content=text))

    return kept
