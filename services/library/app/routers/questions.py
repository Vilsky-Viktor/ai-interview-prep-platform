from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser
from app.schemas.feedback import (
    MyReportOut,
    QuestionRatingIn,
    QuestionRatingOut,
    ReportIn,
    ReportOut,
)
from app.services.access import require_member, require_owner
from app.storage import feedback, preparations

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/{question_id}/rating")
async def get_rating(question_id: UUID, user: CurrentUser) -> QuestionRatingOut:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    return QuestionRatingOut(value=await feedback.my_question_rating(question_id, user.uid))


@router.put("/{question_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
async def rate(question_id: UUID, body: QuestionRatingIn, user: CurrentUser) -> None:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    if not await feedback.rate_question(question_id, user.uid, body.value):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already rated")


@router.get("/{question_id}/reports")
async def list_reports(question_id: UUID, user: CurrentUser) -> list[ReportOut]:
    """Only the preparation owner reads reports; interview reports go through companies."""
    require_owner(await preparations.get_for_question(question_id), user.uid)

    reports = await feedback.list_reports(question_id)

    return [ReportOut.model_validate(report, from_attributes=True) for report in reports]


@router.post("/{question_id}/reports", status_code=status.HTTP_201_CREATED)
async def report(question_id: UUID, body: ReportIn, user: CurrentUser) -> None:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    if not await feedback.report_question(question_id, user.uid, body.reason, body.comment):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already reported")


@router.get("/{question_id}/reports/mine")
async def my_report(question_id: UUID, user: CurrentUser) -> MyReportOut:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    return MyReportOut(reported=await feedback.has_reported(question_id, user.uid))
