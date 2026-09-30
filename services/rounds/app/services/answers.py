import logging

from fastapi import HTTPException, status

from app.config.settings import settings
from app.constants.rounds import GRADING_FAILED, Mode, RoundStatus
from app.helpers.rate_limit import hit
from app.helpers.rounds import correct_option_index, find_question
from app.helpers.scores import current_score
from app.integrations.redis import get_redis
from app.models.rounds import Answer, Round
from app.schemas.rounds import AnswerCreate, AnswerResult
from app.services.grading import grade_open_answer
from app.storage import rounds

logger = logging.getLogger(__name__)


async def submit_answer(round_: Round, body: AnswerCreate) -> AnswerResult:
    if round_.status != RoundStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_409_CONFLICT, "Round is finished")

    question = find_question(round_, str(body.question_id))

    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not in this round")

    if any(answer.question_id == body.question_id for answer in round_.answers):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    answer = Answer(round_id=round_.id, question_id=body.question_id)
    correct_index = correct_option_index(question)

    if round_.mode == Mode.CHOICE:
        if body.option_index is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "option_index is required")

        answer.option_index = body.option_index
        answer.correct = body.option_index == correct_index
        answer.score = 100 if answer.correct else 0
    else:
        if not (body.text or "").strip():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "text is required")

        answer.text = body.text.strip()
        await hit(
            get_redis(),
            f"rate:llm:{round_.user_id}",
            settings.llm_limit,
            settings.llm_window_seconds,
        )

        try:
            grade = await grade_open_answer(question, answer.text)
        except Exception:
            logger.exception("Grading failed for round %s", round_.id)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, GRADING_FAILED)

        answer.score = grade.score
        answer.feedback = grade.feedback

    if not await rounds.add_answer(answer):
        raise HTTPException(status.HTTP_409_CONFLICT, "Question already answered")

    scores = [previous.score for previous in round_.answers] + [answer.score]

    return AnswerResult(
        answer_id=answer.id,
        correct=answer.correct,
        score=answer.score,
        feedback=answer.feedback,
        reference_answer=question["reference_answer"],
        correct_option_index=correct_index if round_.mode == Mode.CHOICE else None,
        current_score=current_score(scores),
        answered=len(scores),
        total=len(round_.questions),
    )
