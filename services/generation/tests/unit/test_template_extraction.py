import asyncio
from types import SimpleNamespace

from app.integrations import llm
from app.services.nodes import extraction
from app.storage import draft_cache


def system_prompt(monkeypatch, template):
    """The extraction instructions the model gets for a test, or for a template."""
    seen = []

    class FakeLLM:
        def with_structured_output(self, schema):
            return self

        async def ainvoke(self, messages):
            seen.append(messages[0].content)

            return SimpleNamespace(title="Accountant", requirements=["IFRS"], level="medium")

    async def no_cache(*args):
        return None

    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM())
    monkeypatch.setattr(draft_cache, "get", no_cache)
    monkeypatch.setattr(draft_cache, "put", no_cache)
    state = {"input_text": "Acme hires an accountant.", "language": "en", "template": template}

    asyncio.run(extraction.extract_info(state))

    return seen[0]


def test_a_template_never_names_the_company_a_test_may(monkeypatch):
    template = system_prompt(monkeypatch, True)
    test = system_prompt(monkeypatch, False)

    assert "Never the company's name" in template
    assert "at Acme" not in template
    assert "Senior Accountant at Acme" in test
