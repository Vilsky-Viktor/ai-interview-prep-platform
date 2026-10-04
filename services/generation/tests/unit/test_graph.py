import asyncio
import re
import uuid
from typing import ClassVar

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from prepza_common.sets import OptionIn, QuestionIn

from app.config.settings import settings
from app.helpers.payload import build_preparation
from app.integrations import library, llm
from app.schemas.extraction import JobExtraction
from app.schemas.questions import QuestionItem, QuestionItemList
from app.schemas.topics import TopicList, TopicStructure
from app.services.graph import build_graph
from app.storage import draft_cache
from tests.unit.test_draft_cache import FakeRedis


class FakeStructured:
    def __init__(self, schema):
        self.schema = schema

    async def ainvoke(self, messages):
        prompt = messages[-1].content

        if self.schema is JobExtraction:
            return JobExtraction(title="Backend", requirements=["Python"], level="medium")

        if self.schema is TopicList:
            return TopicList(
                topics=[
                    TopicStructure(main_topic="Python", subtopics=["Asyncio", "Typing"]),
                    TopicStructure(main_topic="SQL", subtopics=["Joins"]),
                ]
            )

        count = int(re.search(r"Number of questions: (\d+)", prompt).group(1))
        subtopic = re.search(r"Subtopic: (.+)", prompt).group(1)
        focus = re.search(r"Focus: (.+)", prompt).group(1)[:12]
        # Every call also writes one question that only rephrases another call's.
        texts = [f"Same meaning, worded by {subtopic} / {focus}"] + [
            f"{subtopic} / {focus} / {i}" for i in range(count - 1)
        ]

        return QuestionItemList(
            items=[
                QuestionItem(
                    question=text,
                    example=None,
                    correct_option="Right",
                    distractors=["W1", "W2", "W3"],
                    ambiguous=False,
                )
                for text in texts
            ]
        )


class FakeLLM:
    def with_structured_output(self, schema):
        return FakeStructured(schema)


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    monkeypatch.setattr(draft_cache, "get_redis", lambda: FakeRedis(down=True))


class FakeEmbeddings:
    """A direction of its own for every text, except rephrasings, which share one."""

    directions: ClassVar[dict[str, int]] = {}

    async def aembed_documents(self, texts):
        vectors = []

        for text in texts:
            key = "same" if text.startswith("Same meaning") else text
            direction = self.directions.setdefault(key, len(self.directions) % 256)
            vectors.append([1.0 if i == direction else 0.0 for i in range(256)])

        return vectors


def reusable(texts):
    """Library offers these proven questions for every topic."""

    async def find(request):
        return [
            QuestionIn(text=text, options=[OptionIn(answer="Yes", correct=True)]) for text in texts
        ]

    return find


async def run_graph(review=None, kind=None):
    graph = build_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "test"}}
    interrupts = []
    start = {"input_text": "Job", "kind": kind}

    async for chunk in graph.astream(start, config, stream_mode="updates"):
        interrupts.extend(chunk.get("__interrupt__", ()))

    assert len(interrupts[0].value["topics"]) == 2

    resume = Command(resume=review or {"selected": [0], "instructions": ""})

    async for _ in graph.astream(resume, config, stream_mode="updates"):
        pass

    return (await graph.aget_state(config)).values


@pytest.mark.parametrize("per_topic", [100, 12])
def test_full_graph(monkeypatch, per_topic):
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM())
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)
    monkeypatch.setattr(library, "find_reusable", reusable([]))
    monkeypatch.setattr(settings, "questions_per_topic", per_topic)

    values = asyncio.run(run_graph())
    [topic] = values["final"]

    assert topic["topic"] == "Python"
    assert len(topic["questions"]) == per_topic
    assert sum(text.startswith("Same meaning") for text in topic["questions"]) == 1
    assert all(len(options) == 4 for options in topic["answer_options"])
    assert (
        len(build_preparation(uuid.uuid4(), "uid", "text", values).topics[0].questions) == per_topic
    )


@pytest.mark.parametrize(
    ("kind", "later"),
    [("preparation", {("preparation", "medium")}), ("interview", {("interview", "medium")})],
)
def test_every_call_chooses_its_model_by_who_its_for_and_the_level(monkeypatch, kind, later):
    calls = []

    def choose(*args):
        calls.append(args)

        return FakeLLM()

    monkeypatch.setattr(llm, "get_generation_llm", choose)
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)
    monkeypatch.setattr(library, "find_reusable", reusable([]))
    monkeypatch.setattr(settings, "questions_per_topic", 10)

    asyncio.run(run_graph(kind=kind))

    # Extraction comes before the level is known; topics, questions and fill-ups know both.
    assert calls[0] == (kind, None)
    assert set(calls[1:]) == later


def test_reused_questions_come_first_and_new_ones_fill_the_rest(monkeypatch):
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM())
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)
    monkeypatch.setattr(library, "find_reusable", reusable(["Proven 1", "Proven 2"]))
    monkeypatch.setattr(settings, "questions_per_topic", 10)

    values = asyncio.run(run_graph())
    [topic] = values["final"]
    payload = build_preparation(uuid.uuid4(), "uid", "text", values)

    assert topic["questions"][:2] == ["Proven 1", "Proven 2"]
    assert len(topic["questions"]) == 10
    assert [question.text for question in payload.topics[0].questions[:2]] == [
        "Proven 1",
        "Proven 2",
    ]
    assert len(payload.topics[0].questions) == 10
    assert payload.topics[0].embedding is not None


def test_generation_goes_on_without_reuse_when_embedding_fails(monkeypatch):
    class BrokenEmbeddings:
        async def aembed_documents(self, texts):
            raise ConnectionError("OpenAI is down")

    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM())
    monkeypatch.setattr(llm, "get_embeddings", BrokenEmbeddings)
    monkeypatch.setattr(settings, "questions_per_topic", 10)

    values = asyncio.run(run_graph())

    assert len(values["final"][0]["questions"]) == 10
    assert build_preparation(uuid.uuid4(), "uid", "text", values).topics[0].embedding is None


def test_topics_edited_by_hand_are_used_without_a_revision(monkeypatch):
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM())
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)
    monkeypatch.setattr(library, "find_reusable", reusable([]))
    monkeypatch.setattr(settings, "questions_per_topic", 10)
    edited = [
        {"main_topic": "Async Python", "subtopics": ["Event loop"]},
        {"main_topic": "SQL", "subtopics": ["Joins"]},
    ]

    values = asyncio.run(run_graph({"selected": [0], "instructions": "", "topics": edited}))
    [topic] = values["final"]

    assert topic["topic"] == "Async Python"
    assert topic["subtopics"] == ["Event loop"]
    assert all(text.startswith(("Event loop", "Same meaning")) for text in topic["questions"])
