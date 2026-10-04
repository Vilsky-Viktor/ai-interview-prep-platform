import asyncio
import uuid

import pytest

from app.integrations import library, llm
from app.schemas.questions import AnswerItem, AnswerList, NewQuestion
from app.schemas.regenerate import QuestionContext
from app.services.regenerate import regenerate

QUESTION_ID = uuid.uuid4()


def context():
    return QuestionContext(
        set_id=uuid.uuid4(),
        kind="preparation",
        owner_id="ann",
        level="medium",
        topic="Python",
        subtopics=["Asyncio"],
        existing=["What is the GIL?", "When is asyncio a good fit?"],
    )


class FakeStructured:
    def __init__(self, schema, questions):
        self.schema = schema
        self.questions = questions

    async def ainvoke(self, messages):
        if self.schema is NewQuestion:
            return NewQuestion(question=self.questions.pop(0), example=None)

        ambiguous = "[0] Which keyword" in messages[0].content

        return AnswerList(
            answers=[
                AnswerItem(
                    id=0, correct_option="Right", distractors=["A", "B", "C"], ambiguous=ambiguous
                )
            ]
        )


class FakeEmbeddings:
    """Texts about the GIL mean the same thing; every other text means something of its own."""

    async def aembed_documents(self, texts):
        meanings = [
            "gil" if "gil" in text.lower() or "interpreter lock" in text.lower() else text
            for text in texts
        ]
        distinct = list(dict.fromkeys(meanings))

        return [
            [float(distinct.index(meaning) == i) for i in range(len(distinct))]
            for meaning in meanings
        ]


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)


class FakeLLM:
    def __init__(self, questions):
        self.questions = questions

    def with_structured_output(self, schema):
        return FakeStructured(schema, self.questions)


def test_skips_duplicates_and_saves_new_question(monkeypatch):
    fake = FakeLLM(["  what is the  GIL? ", "How do you cancel an asyncio task?"])
    saved = {}

    async def fake_replace(question_id, question):
        saved["id"] = question_id
        saved["question"] = question

    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    result = asyncio.run(regenerate(QUESTION_ID, context()))

    assert result.text == "How do you cancel an asyncio task?"
    assert saved["id"] == QUESTION_ID
    assert sum(option.correct for option in saved["question"].options) == 1


def test_skips_a_rephrased_existing_question(monkeypatch):
    fake = FakeLLM(["What does the global interpreter lock do?", "What does asyncio.run do?"])
    saved = {}

    async def fake_replace(question_id, question):
        saved["question"] = question

    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    result = asyncio.run(regenerate(QUESTION_ID, context()))

    assert result.text == "What does asyncio.run do?"
    assert saved["question"].text == "What does asyncio.run do?"


def test_ambiguous_question_is_replaced_by_another(monkeypatch):
    fake = FakeLLM(["Which keyword handles exceptions?", "What does asyncio.gather return?"])
    saved = {}

    async def fake_replace(question_id, question):
        saved["question"] = question

    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    result = asyncio.run(regenerate(QUESTION_ID, context()))

    assert result.text == "What does asyncio.gather return?"
    assert saved["question"].text == "What does asyncio.gather return?"


def test_gives_up_when_every_attempt_duplicates(monkeypatch):
    fake = FakeLLM(["What is the GIL?"] * 3)

    async def fake_replace(question_id, question):
        raise AssertionError("must not save a duplicate")

    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    assert asyncio.run(regenerate(QUESTION_ID, context())) is None
