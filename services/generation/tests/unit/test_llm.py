from app.config.settings import settings
from app.constants.generation import LLM_TIMEOUT_SECONDS
from app.integrations import llm


def test_llm_calls_time_out(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    llm.build_llm.cache_clear()

    try:
        assert llm.get_generation_llm().request_timeout == LLM_TIMEOUT_SECONDS
    finally:
        llm.build_llm.cache_clear()


def test_each_task_uses_its_own_model_and_effort(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(settings, "generation_model", "model-a")
    monkeypatch.setattr(settings, "generation_reasoning_effort", "high")
    monkeypatch.setattr(settings, "verify_model", "model-b")
    monkeypatch.setattr(settings, "verify_reasoning_effort", "minimal")
    monkeypatch.setattr(settings, "title_check_model", "model-c")
    monkeypatch.setattr(settings, "title_check_reasoning_effort", "none")
    llm.build_llm.cache_clear()

    try:
        tasks = [llm.get_generation_llm(), llm.get_verifier_llm(), llm.get_title_check_llm()]

        assert [(t.model_name, t.reasoning_effort) for t in tasks] == [
            ("model-a", "high"),
            ("model-b", "minimal"),
            ("model-c", "none"),
        ]
    finally:
        llm.build_llm.cache_clear()
