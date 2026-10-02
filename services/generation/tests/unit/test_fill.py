import asyncio
import uuid

import pytest

from app.config.settings import settings
from app.helpers.payload import build_preparation
from app.integrations import llm
from app.schemas.questions import QuestionItem, QuestionItemList
from app.services.nodes.fill import TopicShortError, fill_topics

OPTIONS = [{"answer": "Right", "correct": True}, {"answer": "Wrong", "correct": False}]


class FakeStructured:
    def __init__(self, schema, questions, prompts):
        self.questions = questions
        self.prompts = prompts

    async def ainvoke(self, messages):
        self.prompts.append(messages[-1].content)

        return QuestionItemList(
            items=[
                QuestionItem(
                    question=text,
                    correct_option="Right",
                    distractors=["A", "B", "C"],
                    ambiguous=False,
                )
                for text in self.questions
            ]
        )


class FakeLLM:
    def __init__(self, questions):
        self.questions = questions
        self.prompts = []

    def with_structured_output(self, schema):
        return FakeStructured(schema, self.questions, self.prompts)


def state(usable, dropped=0):
    """One topic with `usable` answered questions and `dropped` ones that have no options."""
    questions = [f"Question {i}" for i in range(usable + dropped)]
    options = [OPTIONS] * usable + [[]] * dropped

    return {
        "level": "basic",
        "title": "Bookkeeping",
        "requirements": [],
        "final": [
            {
                "topic": "Bookkeeping",
                "subtopics": ["Cash"],
                "questions": questions,
                "answer_options": options,
            }
        ],
    }


@pytest.fixture(autouse=True)
def ten_per_topic(monkeypatch):
    monkeypatch.setattr(settings, "questions_per_topic", 10)


def test_a_short_topic_is_filled_to_exactly_its_size(monkeypatch):
    # One returned question repeats an existing one, so only three are new.
    fake = FakeLLM(["Question 0", "New 1", "New 2", "New 3"])
    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    values = state(usable=7, dropped=2)

    values.update(asyncio.run(fill_topics(values)))
    payload = build_preparation(uuid.uuid4(), "uid", "text", values)

    assert [q.text for q in payload.topics[0].questions][-3:] == ["New 1", "New 2", "New 3"]
    assert len(payload.topics[0].questions) == 10
    assert "- Question 8" in fake.prompts[0]


def test_a_full_topic_is_left_alone(monkeypatch):
    fake = FakeLLM(["Never asked"])
    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    values = state(usable=10)

    assert asyncio.run(fill_topics(values))["final"] == values["final"]
    assert fake.prompts == []


def test_a_topic_that_cannot_be_filled_fails_the_generation(monkeypatch):
    fake = FakeLLM(["Question 0", "Question 1"])
    monkeypatch.setattr(llm, "get_llm", lambda: fake)

    with pytest.raises(TopicShortError):
        asyncio.run(fill_topics(state(usable=8)))

    assert len(fake.prompts) == 3
