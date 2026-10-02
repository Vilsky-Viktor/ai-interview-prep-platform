from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.integrations import generation
from app.schemas.feedback import (
    MyReportOut,
    QuestionRatingIn,
    QuestionRatingOut,
    ReportIn,
    ReportOut,
)
from app.services.access import require_member, require_owner
from app.services.quality import review
from app.storage import feedback, preparations

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/{question_id}/regenerate")
async def regenerate(question_id: UUID, user: CurrentUser) -> dict:
    """Only the owner of a preparation replaces its questions; generation writes the new one."""
    question_set = require_owner(await preparations.get_for_question(question_id), user.uid)
    response = await generation.regenerate_question(question_id, question_set.id, user.uid)

    # Keeps generation's rate limit (429) and failures for the client.
    if response.is_error:
        raise HTTPException(response.status_code, response.json().get("detail"))

    return response.json()


@router.get("/{question_id}/rating")
async def get_rating(question_id: UUID, user: CurrentUser) -> QuestionRatingOut:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    return QuestionRatingOut(value=await feedback.my_question_rating(question_id, user.uid))


@router.put("/{question_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
async def rate(question_id: UUID, body: QuestionRatingIn, user: CurrentUser) -> None:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    await feedback.rate_question(question_id, user.uid, body.value)

    await review(question_id)


@router.get("/{question_id}/reports")
async def list_reports(question_id: UUID, user: CurrentUser, page: PageParams) -> list[ReportOut]:
    """Only the preparation owner reads reports; interview reports go through companies."""
    require_owner(await preparations.get_for_question(question_id), user.uid)

    reports = await feedback.list_reports(question_id, page.offset, page.limit)

    return [ReportOut.model_validate(report, from_attributes=True) for report in reports]


@router.post("/{question_id}/reports", status_code=status.HTTP_201_CREATED)
async def report(question_id: UUID, body: ReportIn, user: CurrentUser) -> None:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    if not await feedback.report_question(question_id, user.uid, body.reason, body.comment):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already reported")

    await review(question_id)


@router.get("/{question_id}/reports/mine")
async def my_report(question_id: UUID, user: CurrentUser) -> MyReportOut:
    await require_member(await preparations.get_for_question(question_id), user.uid)

    return MyReportOut(reported=await feedback.has_reported(question_id, user.uid))
