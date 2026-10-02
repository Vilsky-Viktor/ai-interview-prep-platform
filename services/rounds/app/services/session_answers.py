from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.constants.rounds import TIME_UP, RoundStatus
from app.helpers.scores import current_score, score_passed
from app.helpers.sessions import answer_seconds, next_session_question
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.schemas.sessions import SessionAnswerResult
from app.services import outbox as outbox_service
from app.services.answers import checked_answer, recorded
from app.storage import sessions


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

    if not await sessions.add_answer(answer, recorded(answer, question)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    await outbox_service.flush_quietly()

    scores = [previous.score for previous in row.answers] + [answer.score]
    result = SessionAnswerResult(
        answer_id=answer.id, answered=len(scores), total=len(row.questions)
    )

    if row.share_results:
        result.correct = answer.correct
        result.current_score = current_score(scores)
        result.passed = score_passed(result.current_score)

    return result
