from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.quality import QuestionQuality, ReportNote
from app.service_auth import ServiceCaller
from app.services import quality as quality_service
from app.storage import feedback, quality

router = APIRouter(prefix="/internal/questions", tags=["internal"])


@router.get("/{question_id}/quality")
async def get_quality(question_id: UUID, caller: ServiceCaller) -> QuestionQuality:
    found = await quality.load(question_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    question, stats = found[0], found[1]
    reports = await feedback.list_reports(question_id)

    return QuestionQuality(
        text=question.text,
        options=question.options,
        answers=stats.answers if stats else 0,
        option_picks=stats.option_picks if stats else {},
        reports=[ReportNote(reason=report.reason, comment=report.comment) for report in reports],
    )


@router.post("/{question_id}/keep", status_code=status.HTTP_204_NO_CONTENT)
async def keep(question_id: UUID, caller: ServiceCaller) -> None:
    """The verifier found nothing wrong: serve the question again and stop flagging it."""
    await quality.save_flag(question_id, None, kept=True)


@router.post("/{question_id}/wrong", status_code=status.HTTP_204_NO_CONTENT)
async def mark_wrong(question_id: UUID, caller: ServiceCaller) -> None:
    """For companies, once it has checked the question is in the company's test."""
    await quality_service.mark_wrong(question_id)
