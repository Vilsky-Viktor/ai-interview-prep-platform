from app.constants.generation import LLM_TIMEOUT_SECONDS
from app.integrations import llm


def test_llm_calls_time_out(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    llm.get_llm.cache_clear()

    try:
        assert llm.get_llm().request_timeout == LLM_TIMEOUT_SECONDS
    finally:
        llm.get_llm.cache_clear()


def test_reasoning_effort_comes_from_the_settings(monkeypatch):
    from app.config.settings import settings

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(settings, "llm_reasoning_effort", "high")
    monkeypatch.setattr(settings, "verify_reasoning_effort", "minimal")
    llm.get_llm.cache_clear()

    try:
        assert llm.get_llm().reasoning_effort == "high"
        assert llm.get_verifier_llm().reasoning_effort == "minimal"
    finally:
        llm.get_llm.cache_clear()
