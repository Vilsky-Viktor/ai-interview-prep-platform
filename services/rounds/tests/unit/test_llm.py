from app.config.settings import settings
from app.constants.rounds import CHAT_TIMEOUT_SECONDS
from app.integrations import llm


def test_the_tutor_and_the_help_chat_use_their_own_models(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    llm.get_tutor_llm.cache_clear()
    llm.get_help_llm.cache_clear()

    try:
        tutor, help_chat = llm.get_tutor_llm(), llm.get_help_llm()

        assert tutor.model_name == settings.tutor_model
        assert tutor.reasoning_effort == settings.tutor_reasoning_effort
        # A reasoning model refuses temperature, so the tutor sends none.
        assert tutor.temperature is None
        assert help_chat.model_name == settings.llm_model
        assert help_chat.reasoning_effort == "none"
        assert tutor.request_timeout == help_chat.request_timeout == CHAT_TIMEOUT_SECONDS
    finally:
        llm.get_tutor_llm.cache_clear()
        llm.get_help_llm.cache_clear()
