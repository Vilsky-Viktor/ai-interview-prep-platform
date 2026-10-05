import pytest

from app.config.settings import settings
from app.constants.generation import LLM_TIMEOUT_SECONDS
from app.integrations import llm


@pytest.fixture(autouse=True)
def models(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(settings, "interview_model", "interview-model")
    llm.build_llm.cache_clear()
    yield
    llm.build_llm.cache_clear()


def test_llm_calls_time_out():
    assert llm.get_generation_llm().request_timeout == LLM_TIMEOUT_SECONDS


def test_each_task_uses_its_own_model_and_effort(monkeypatch):
    monkeypatch.setattr(settings, "interview_reasoning_effort", "high")
    monkeypatch.setattr(settings, "verify_model", "model-b")
    monkeypatch.setattr(settings, "verify_reasoning_effort", "minimal")
    tasks = [llm.get_generation_llm(), llm.get_verifier_llm()]

    assert [(t.model_name, t.reasoning_effort) for t in tasks] == [
        ("interview-model", "high"),
        ("model-b", "minimal"),
    ]
