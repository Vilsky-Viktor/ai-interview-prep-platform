import pytest

from app.config.settings import settings
from app.constants.generation import LLM_TIMEOUT_SECONDS
from app.integrations import llm


@pytest.fixture(autouse=True)
def models(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(settings, "interview_model", "interview-model")
    monkeypatch.setattr(settings, "kit_model", "kit-model")
    monkeypatch.setattr(settings, "hard_kit_model", "hard-kit-model")
    llm.build_llm.cache_clear()
    yield
    llm.build_llm.cache_clear()


def test_llm_calls_time_out():
    assert llm.get_generation_llm("preparation", "basic").request_timeout == LLM_TIMEOUT_SECONDS


@pytest.mark.parametrize(
    ("kind", "level", "model"),
    [
        # Interviews are judged on, so they never get the cheaper model, at any level.
        ("interview", "basic", "interview-model"),
        ("interview", "hard", "interview-model"),
        ("interview", None, "interview-model"),
        ("preparation", "basic", "kit-model"),
        ("preparation", "medium", "kit-model"),
        ("preparation", "hard", "hard-kit-model"),
        # Before extraction knows the level, and for runs started before kinds were passed.
        ("preparation", None, "hard-kit-model"),
        (None, "basic", "hard-kit-model"),
    ],
)
def test_generation_model_follows_who_its_for_and_the_level(kind, level, model):
    assert llm.get_generation_llm(kind, level).model_name == model


def test_each_task_uses_its_own_model_and_effort(monkeypatch):
    monkeypatch.setattr(settings, "kit_reasoning_effort", "high")
    monkeypatch.setattr(settings, "verify_model", "model-b")
    monkeypatch.setattr(settings, "verify_reasoning_effort", "minimal")
    monkeypatch.setattr(settings, "title_check_model", "model-c")
    monkeypatch.setattr(settings, "title_check_reasoning_effort", "none")
    tasks = [
        llm.get_generation_llm("preparation", "medium"),
        llm.get_verifier_llm(),
        llm.get_title_check_llm(),
    ]

    assert [(t.model_name, t.reasoning_effort) for t in tasks] == [
        ("kit-model", "high"),
        ("model-b", "minimal"),
        ("model-c", "none"),
    ]
