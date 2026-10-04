from app.config.settings import settings
from app.constants.rounds import CHAT_TIMEOUT_SECONDS
from app.integrations import llm


def clear():
    llm.get_tutor_llm.cache_clear()
    llm.get_help_llm.cache_clear()


def test_the_tutor_and_the_help_chat_use_their_own_models(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    clear()

    try:
        tutor, help_chat = llm.get_tutor_llm(), llm.get_help_llm()

        assert tutor.model_name == settings.tutor_model
        assert tutor.reasoning_effort == settings.tutor_reasoning_effort
        # A reasoning model refuses temperature, so the tutor sends none.
        assert tutor.temperature is None
        assert help_chat.model_name == settings.help_model
        assert help_chat.reasoning_effort == settings.help_reasoning_effort == "none"
        assert help_chat.temperature == 0.3
        assert tutor.request_timeout == help_chat.request_timeout == CHAT_TIMEOUT_SECONDS
    finally:
        clear()


def test_the_help_chat_sends_no_temperature_when_it_reasons(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(settings, "help_reasoning_effort", "low")
    clear()

    try:
        assert llm.get_help_llm().temperature is None
    finally:
        clear()
