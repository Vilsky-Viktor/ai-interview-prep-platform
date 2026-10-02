import asyncio
import uuid

import pytest
from fastapi import HTTPException

from app.helpers.rounds import next_question
from app.integrations import events
from app.models.rounds import Answer, Round
from app.schemas.rounds import AnswerCreate
from app.services.answers import submit_answer
from app.storage import progress, rounds

Q1, Q2 = uuid.uuid4(), uuid.uuid4()


def make_round(status: str = "in_progress") -> Round:
    options = [
        {"answer": "Wrong", "correct": False},
        {"answer": "Right", "correct": True},
        {"answer": "Wrong 2", "correct": False},
        {"answer": "Wrong 3", "correct": False},
    ]
    questions = [
        {"id": str(q), "text": f"Question {n}", "options": options}
        for n, q in enumerate((Q1, Q2), start=1)
    ]

    return Round(
        id=uuid.uuid4(), user_id="u1", status=status, questions=questions, answers=[]
    )


@pytest.fixture(autouse=True)
def published(monkeypatch):
    sent = []

    async def publish(event_type, data):
        sent.append((event_type, data))

    monkeypatch.setattr(events, "publish", publish)

    return sent


@pytest.fixture(autouse=True)
def rebuilt(monkeypatch):
    calls = []

    async def add_answer(answer):
        answer.id = uuid.uuid4()

        return True

    async def rebuild(user_id, question_ids):
        calls.append((user_id, question_ids))

    monkeypatch.setattr(rounds, "add_answer", add_answer)
    monkeypatch.setattr(progress, "rebuild", rebuild)

    return calls


def test_next_question_skips_answered_and_hides_answers():
    round_ = make_round()
    round_.answers = [Answer(question_id=Q1, option_index=1, correct=True, score=100)]

    question = next_question(round_)

    assert question.question_id == Q2
    assert question.number == 2
    assert question.options == ["Wrong", "Right", "Wrong 2", "Wrong 3"]


def test_right_option_is_correct():
    result = asyncio.run(submit_answer(make_round(), AnswerCreate(question_id=Q1, option_index=1)))

    assert result.correct is True
    assert result.correct_option_index == 1
    assert (result.current_score, result.answered, result.total) == (100, 1, 2)


def test_wrong_option_lowers_the_score():
    round_ = make_round()
    round_.answers = [Answer(question_id=Q2, option_index=1, correct=True, score=100)]
    result = asyncio.run(submit_answer(round_, AnswerCreate(question_id=Q1, option_index=0)))

    assert result.correct is False
    assert result.correct_option_index == 1
    assert (result.current_score, result.answered, result.total) == (50, 2, 2)


def test_rejects_second_answer_to_same_question():
    round_ = make_round()
    round_.answers = [Answer(question_id=Q1, option_index=0, correct=False, score=0)]

    with pytest.raises(HTTPException) as error:
        asyncio.run(submit_answer(round_, AnswerCreate(question_id=Q1, option_index=0)))

    assert error.value.status_code == 409


def test_rejects_answers_to_a_finished_round():
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            submit_answer(make_round("finished"), AnswerCreate(question_id=Q1, option_index=1))
        )

    assert error.value.status_code == 409


def test_option_index_is_required():
    with pytest.raises(ValueError):
        AnswerCreate(question_id=Q1)


def test_answer_counts_towards_progress_before_the_round_finishes(rebuilt):
    asyncio.run(submit_answer(make_round(), AnswerCreate(question_id=Q1, option_index=0)))

    assert rebuilt == [("u1", [Q1])]


def test_answer_is_announced_with_the_picked_option(published):
    asyncio.run(submit_answer(make_round(), AnswerCreate(question_id=Q1, option_index=0)))

    assert published == [
        (
            "answer.recorded",
            {
                "question_id": str(Q1),
                "question_text": "Question 1",
                "option": "Wrong",
                "correct": False,
            },
        )
    ]


def test_answering_works_even_if_the_event_cannot_be_published(monkeypatch):
    async def redis_down(event_type, data):
        raise ConnectionError("redis is down")

    monkeypatch.setattr(events, "publish", redis_down)

    result = asyncio.run(submit_answer(make_round(), AnswerCreate(question_id=Q1, option_index=1)))

    assert result.correct is True
