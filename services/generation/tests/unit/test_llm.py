from app.constants.generation import LLM_TIMEOUT_SECONDS
from app.integrations import llm


def test_llm_calls_time_out(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    llm.get_llm.cache_clear()

    try:
        assert llm.get_llm().request_timeout == LLM_TIMEOUT_SECONDS
    finally:
        llm.get_llm.cache_clear()
