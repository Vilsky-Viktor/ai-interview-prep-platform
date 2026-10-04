import asyncio
from types import SimpleNamespace

from app.integrations import llm
from app.schemas.extraction import JobExtraction
from app.services.nodes.extraction import extract_info
from app.storage import draft_cache


class FakeRedis:
    def __init__(self, down=False):
        self.values = {}
        self.down = down

    async def get(self, key):
        if self.down:
            raise ConnectionError("Redis is down")

        return self.values.get(key)

    async def set(self, key, value, ex):
        if self.down:
            raise ConnectionError("Redis is down")

        self.values[key] = value


class CountingLLM:
    model_name = "model-a"
    reasoning_effort = "low"

    def __init__(self):
        self.calls = 0

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, messages):
        self.calls += 1

        return JobExtraction(title="Accountant", requirements=["Bookkeeping"], level="basic")


def run_twice(monkeypatch, redis):
    fake = CountingLLM()
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: fake)
    monkeypatch.setattr(draft_cache, "get_redis", lambda: redis)

    first = asyncio.run(extract_info({"input_text": "Junior accountant"}))
    again = asyncio.run(extract_info({"input_text": "Junior accountant"}))

    return first, again, fake.calls


def test_the_same_text_is_extracted_once(monkeypatch):
    first, again, calls = run_twice(monkeypatch, FakeRedis())

    assert first == again
    assert first == {"title": "Accountant", "requirements": ["Bookkeeping"], "level": "basic"}
    assert calls == 1


def test_without_redis_every_generation_calls_the_model(monkeypatch):
    first, again, calls = run_twice(monkeypatch, FakeRedis(down=True))

    assert first == again
    assert calls == 2


def test_another_model_effort_or_prompt_gets_another_key():
    def model(name, effort):
        return SimpleNamespace(model_name=name, reasoning_effort=effort)

    key = draft_cache.cache_key("topics", "prompt A", model("sol", "low"))

    assert key != draft_cache.cache_key("topics", "prompt B", model("sol", "low"))
    # A learner's draft on another model never serves a company's interview.
    assert key != draft_cache.cache_key("topics", "prompt A", model("luna", "low"))
    assert key != draft_cache.cache_key("topics", "prompt A", model("sol", "high"))
