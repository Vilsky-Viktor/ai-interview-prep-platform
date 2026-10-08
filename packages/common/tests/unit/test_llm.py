import pytest
from prepza_common.llm import chat_model


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
