import asyncio
import uuid

import pytest
from langchain_core.messages import AIMessage

from app.helpers.titles import clean_title, should_title
from app.models.answers import Turn
from app.services import titles

TURN = Turn(uuid.uuid4(), "ann", None, "t", "de")


@pytest.mark.parametrize(
    "questions, due", [(0, False), (1, True), (2, False), (4, False), (5, True), (10, True)]
)
def test_a_title_comes_after_the_first_answer_and_every_fifth_question(questions, due):
    assert should_title(questions) is due


@pytest.mark.parametrize(
    "text, title",
    [
        ('"Hiring a backend developer."', "Hiring a backend developer"),
        ("Invite ann@example.com to Backend\nmore", "Invite  to Backend"),
        ("x" * 80, "x" * 60),
        ("  ", None),
    ],
)
def test_the_models_title_is_one_clean_line(text, title):
    assert clean_title(text) == title


@pytest.fixture
def stored(monkeypatch):
    kept = []
    spent = []

    async def count(conversation_id):
        return stored.questions

    async def recent(conversation_id, limit):
        return []

    async def set_title(conversation_id, title):
        kept.append(title)

    async def record(redis, user_id, company_id, tokens):
        spent.append(tokens)

    stored.questions = 1
    monkeypatch.setattr(titles.messages, "count_questions", count)
    monkeypatch.setattr(titles.messages, "recent", recent)
    monkeypatch.setattr(titles.conversations, "set_title", set_title)
    monkeypatch.setattr(titles.limits, "record", record)

    return kept, spent


class TitleModel:
    def __init__(self, reply):
        self.reply = reply

    async def ainvoke(self, messages):
        if isinstance(self.reply, Exception):
            raise self.reply

        return self.reply


def test_the_title_is_saved_and_its_tokens_count(stored, monkeypatch):
    kept, spent = stored
    reply = AIMessage(
        content="Backend hiring",
        usage_metadata={"input_tokens": 30, "output_tokens": 4, "total_tokens": 34},
    )
    monkeypatch.setattr(titles.llm, "get_title_model", lambda: TitleModel(reply))

    assert asyncio.run(titles.refresh(TURN)) == "Backend hiring"
    assert (kept, spent) == (["Backend hiring"], [34])


def test_a_failed_title_keeps_the_old_one(stored, monkeypatch):
    kept, _ = stored
    monkeypatch.setattr(titles.llm, "get_title_model", lambda: TitleModel(RuntimeError("down")))

    assert asyncio.run(titles.refresh(TURN)) is None
    assert kept == []


def test_no_call_between_the_trigger_points(stored, monkeypatch):
    stored_questions = 3
    monkeypatch.setattr(titles.messages, "count_questions", lambda _: _count(stored_questions))
    monkeypatch.setattr(titles.llm, "get_title_model", lambda: pytest.fail("called"))

    assert asyncio.run(titles.refresh(TURN)) is None


async def _count(value):
    return value
