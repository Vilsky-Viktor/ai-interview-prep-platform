import logging

from fastapi import HTTPException, status

from app.constants.events import ANSWER_RECORDED
from app.constants.rounds import CORRECT_SCORE, RoundStatus
from app.helpers.rounds import correct_option_index, find_question
from app.helpers.scores import current_score, score_passed
from app.integrations import events
from app.models.rounds import Answer, Round
from app.schemas.rounds import AnswerCreate, AnswerResult
from app.storage import progress, rounds

logger = logging.getLogger(__name__)


async def announce(answer: Answer, question: dict) -> None:
    """Tells library which option was picked, for the question's statistics.

    Statistics never block answering: a failure is only logged.
    """
    try:
        await events.publish(
            ANSWER_RECORDED,
            {
                "question_id": str(answer.question_id),
                "question_text": question["text"],
                "option": question["options"][answer.option_index]["answer"],
                "correct": answer.correct,
            },
        )
    except Exception:
        logger.exception("Couldn't publish the answer to question %s", answer.question_id)


def checked_answer(row, body: AnswerCreate) -> tuple[Answer, dict]:
    """The checked answer to one question of a round or session, and that question."""
    if row.status != RoundStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already finished")

    question = find_question(row, str(body.question_id))

    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    if any(answer.question_id == body.question_id for answer in row.answers):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    correct = body.option_index == correct_option_index(question)
    answer = Answer(
        question_id=body.question_id,
        option_index=body.option_index,
        correct=correct,
        score=CORRECT_SCORE if correct else 0,
    )

    return answer, question


async def submit_answer(round_: Round, body: AnswerCreate) -> AnswerResult:
    answer, question = checked_answer(round_, body)
    answer.round_id = round_.id

    if not await rounds.add_answer(answer):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    # Counts towards the topic's progress right away, not only once the round finishes.
    await progress.rebuild(round_.user_id, [answer.question_id])
    await announce(answer, question)
    scores = [previous.score for previous in round_.answers] + [answer.score]

    return AnswerResult(
        answer_id=answer.id,
        correct=answer.correct,
        correct_option_index=correct_option_index(question),
        current_score=current_score(scores),
        passed=score_passed(current_score(scores)),
        answered=len(scores),
        total=len(round_.questions),
    )
