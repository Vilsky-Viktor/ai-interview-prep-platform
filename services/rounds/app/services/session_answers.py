import logging

from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.rounds import GRADING_FAILED, Mode, RoundStatus
from app.helpers.rate_limit import hit
from app.helpers.rounds import correct_option_index, find_question
from app.helpers.scores import current_score
from app.integrations.redis import get_redis
from app.models.rounds import Answer
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.schemas.sessions import SessionAnswerResult
from app.services.grading import grade_open_answer
from app.storage import sessions

logger = logging.getLogger(__name__)


async def submit_session_answer(row: Session, body: AnswerCreate) -> SessionAnswerResult:
    if row.status != RoundStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, "Session is finished")

    question = find_question(row, str(body.question_id))

    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not in this session")

    if any(answer.question_id == body.question_id for answer in row.answers):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    answer = Answer(session_id=row.id, question_id=body.question_id)

    if row.mode == Mode.CHOICE:
        if body.option_index is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "option_index is required")

        answer.option_index = body.option_index
        answer.correct = body.option_index == correct_option_index(question)
        answer.score = 100 if answer.correct else 0
    else:
        if not (body.text or "").strip():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "text is required")

        answer.text = body.text.strip()
        await hit(
            get_redis(),
            f"rate:llm:{row.user_id}",
            settings.llm_limit,
            settings.llm_window_seconds,
        )

        try:
            grade = await grade_open_answer(question, answer.text)
        except Exception:
            logger.exception("Grading failed for session %s", row.id)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, GRADING_FAILED)

        answer.score = grade.score
        answer.feedback = grade.feedback

    if not await sessions.add_answer(answer):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    scores = [previous.score for previous in row.answers] + [answer.score]
    result = SessionAnswerResult(answer_id=answer.id, answered=len(scores), total=len(row.questions))

    if row.share_results:
        result.correct = answer.correct
        result.score = answer.score
        result.feedback = answer.feedback
        result.current_score = current_score(scores)

    return result
