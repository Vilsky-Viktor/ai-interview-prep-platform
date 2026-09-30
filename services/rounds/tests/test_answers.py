import asyncio
import uuid

import pytest
from fastapi import HTTPException

from app.helpers.rounds import next_question
from app.integrations import llm
from app.models.rounds import Answer, Round
from app.schemas.grade import Grade
from app.schemas.rounds import AnswerCreate
from app.services.answers import submit_answer
from app.storage import rounds

Q1, Q2 = uuid.uuid4(), uuid.uuid4()


def make_round(mode: str) -> Round:
    options = [
        {"answer": "Wrong", "correct": False},
        {"answer": "Right", "correct": True},
        {"answer": "Wrong 2", "correct": False},
        {"answer": "Wrong 3", "correct": False},
    ]
    questions = [
        {"id": str(q), "text": f"Question {n}", "reference_answer": "Ref", "options": options}
        for n, q in enumerate((Q1, Q2), start=1)
    ]

    return Round(
        id=uuid.uuid4(), mode=mode, status="in_progress", questions=questions, answers=[]
    )


@pytest.fixture(autouse=True)
def fake_storage(monkeypatch):
    async def add_answer(answer):
        answer.id = uuid.uuid4()

        return True

    monkeypatch.setattr(rounds, "add_answer", add_answer)


def test_next_question_skips_answered_and_hides_answers():
    round_ = make_round("choice")
    round_.answers = [Answer(question_id=Q1, score=100)]

    question = next_question(round_)

    assert question.question_id == Q2
    assert question.number == 2
    assert question.options == ["Wrong", "Right", "Wrong 2", "Wrong 3"]


def test_choice_answer():
    result = asyncio.run(
        submit_answer(make_round("choice"), AnswerCreate(question_id=Q1, option_index=1))
    )

    assert result.correct is True
    assert result.score == 100
    assert result.correct_option_index == 1
    assert result.reference_answer == "Ref"


def test_open_answer_is_graded(monkeypatch):
    class FakeGrader:
        async def ainvoke(self, messages):
            return Grade(score=140, feedback=" Good. ")

    class FakeLLM:
        def with_structured_output(self, schema):
            return FakeGrader()

    monkeypatch.setattr(llm, "get_grader_llm", FakeLLM)

    round_ = make_round("open")
    round_.answers = [Answer(question_id=Q2, score=50)]
    result = asyncio.run(submit_answer(round_, AnswerCreate(question_id=Q1, text="My answer")))

    assert (result.score, result.feedback) == (100, "Good.")
    assert result.correct_option_index is None
    assert (result.current_score, result.answered, result.total) == (75, 2, 2)


def test_rejects_second_answer_to_same_question():
    round_ = make_round("choice")
    round_.answers = [Answer(question_id=Q1, score=0)]

    with pytest.raises(HTTPException) as error:
        asyncio.run(submit_answer(round_, AnswerCreate(question_id=Q1, option_index=0)))

    assert error.value.status_code == 409


def test_open_round_requires_text():
    with pytest.raises(HTTPException) as error:
        asyncio.run(submit_answer(make_round("open"), AnswerCreate(question_id=Q1, text=" ")))

    assert error.value.status_code == 422
