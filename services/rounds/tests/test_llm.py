from app.constants.rounds import CHAT_TIMEOUT_SECONDS
from app.integrations import llm


def test_chat_calls_time_out(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    llm.get_chat_llm.cache_clear()

    try:
        assert llm.get_chat_llm().request_timeout == CHAT_TIMEOUT_SECONDS
    finally:
        llm.get_chat_llm.cache_clear()
