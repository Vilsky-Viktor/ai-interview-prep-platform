from fastapi import HTTPException, status

from app.constants.rounds import TIME_UP, RoundStatus
from app.helpers.scores import current_score
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.schemas.sessions import SessionAnswerResult
from app.services.answers import announce, checked_answer
from app.storage import sessions


async def submit_session_answer(row: Session, body: AnswerCreate) -> SessionAnswerResult:
    """Candidates see whether they were right only when the interview shares results."""
    if row.status != RoundStatus.IN_PROGRESS:
        raise HTTPException(
            status.HTTP_409_CONFLICT, TIME_UP if row.deadline else "This section is finished"
        )

    answer, question = checked_answer(row, body)
    answer.session_id = row.id

    if not await sessions.add_answer(answer):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    await announce(answer, question)

    scores = [previous.score for previous in row.answers] + [answer.score]
    result = SessionAnswerResult(answer_id=answer.id, answered=len(scores), total=len(row.questions))

    if row.share_results:
        result.correct = answer.correct
        result.current_score = current_score(scores)

    return result
