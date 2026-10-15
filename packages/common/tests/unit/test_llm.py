import pytest
from langchain_core.messages import AIMessage, HumanMessage
from prepza_common.llm import call_cost, chat_model, latest_messages


@pytest.fixture(autouse=True)
def openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")


def test_a_model_takes_a_temperature_at_effort_none():
    model = chat_model("model-a", "none", temperature=0.3, timeout=60, max_retries=3)

    assert (model.model_name, model.reasoning_effort, model.temperature) == ("model-a", "none", 0.3)
    assert (model.request_timeout, model.max_retries) == (60, 3)


@pytest.mark.parametrize("effort", ["minimal", "low", "medium", "high"])
def test_a_reasoning_model_gets_no_temperature(effort):
    model = chat_model("model-a", effort, temperature=0.3)

    assert model.reasoning_effort == effort
    assert model.temperature is None


def test_without_a_temperature_none_is_sent():
    assert chat_model("model-a", "none").temperature is None


def test_nothing_is_stored_at_openai():
    assert chat_model("model-a", "low").store is False


def test_a_call_costs_its_tokens_at_the_models_price():
    usage = {"input_tokens": 1_000_000, "output_tokens": 100_000}

    assert call_cost("gpt-6.1-sol", usage) == 2.0 + 1.0
    assert call_cost("unknown-model", usage) is None


def test_only_the_latest_messages_that_fit_are_kept():
    messages = [(True, "x" * 50), (False, "y" * 30), (True, "z" * 30)]

    assert latest_messages(messages, 70) == [
        AIMessage(content="y" * 30),
        HumanMessage(content="z" * 30),
    ]


def test_a_message_without_text_adds_nothing():
    assert latest_messages([(True, "Hi"), (False, "")], 1_000) == [HumanMessage(content="Hi")]
