from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.constants.events import ANSWER_RECORDED
from app.constants.rounds import CORRECT_SCORE, TIME_UP, RoundStatus
from app.helpers.rounds import correct_option_index, find_question
from app.helpers.sessions import answer_seconds, next_session_question
from app.models.answers import Answer
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.schemas.sessions import SessionAnswerResult
from app.services import outbox as outbox_service
from app.storage import sessions


def recorded(answer: Answer, question: dict) -> tuple[str, dict]:
    """The event telling library which option was picked, for the question's statistics; it's
    saved with the answer (see storage add_answer) and published right after."""
    return (
        ANSWER_RECORDED,
        {
            "question_id": str(answer.question_id),
            "question_text": question["text"],
            "option": question["options"][answer.option_index]["answer"],
            "correct": answer.correct,
        },
    )


def checked_answer(row, body: AnswerCreate) -> tuple[Answer, dict]:
    """The checked answer to one question of a session, and that question."""
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


async def submit_session_answer(row: Session, body: AnswerCreate) -> SessionAnswerResult:
    """Candidates see whether they were right only when the interview shares results."""
    if row.status != RoundStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, "This section is finished")

    if any(
        answer.question_id == body.question_id and answer.option_index is None
        for answer in row.answers
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, TIME_UP)

    shown = next_session_question(row)

    # Only the question on screen, so its clock always runs while it is answered.
    if row.question_shown_at is None or shown is None or shown.question_id != body.question_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "This question isn't open")

    answer, question = checked_answer(row, body)
    answer.session_id = row.id
    answer.seconds = answer_seconds(row.question_shown_at, datetime.now(UTC))

    # A preview's answers say nothing about a question's quality (a talent's later practice
    # rounds are previews too: they repeat questions whose answers were shown).
    event = None if row.preview else recorded(answer, question)

    if not await sessions.add_answer(answer, event):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    await outbox_service.flush_quietly()

    return SessionAnswerResult(
        answer_id=answer.id, answered=len(row.answers) + 1, total=len(row.questions)
    )
