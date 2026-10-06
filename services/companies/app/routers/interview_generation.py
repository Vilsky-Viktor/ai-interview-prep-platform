from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.audit import AuditAction
from app.integrations import generation as generation_api
from app.models.interviews import Interview
from app.schemas.interviews import ReviewIn
from app.services.access import require_company, require_editor
from app.storage import audit, interviews

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def get_interview(interview_id: UUID) -> Interview:
    interview = await interviews.get(interview_id)

    # A test made from a template has no generation to follow.
    if interview is None or interview.generation_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    return interview


def passed_through(response: httpx.Response) -> dict:
    """Keeps the generation service's 404, 409 (wrong state) and 422 (invalid) for the client."""
    if response.status_code in (
        status.HTTP_404_NOT_FOUND,
        status.HTTP_409_CONFLICT,
        status.HTTP_422_UNPROCESSABLE_CONTENT,
    ):
        raise HTTPException(response.status_code, response.json().get("detail"))

    response.raise_for_status()

    return response.json()


@router.get("/{interview_id}/generation")
async def get_generation(interview_id: UUID, user: CurrentUser) -> dict:
    """Every company member follows the generation, not only the admin who started it."""
    interview = await get_interview(interview_id)
    await require_company(user, interview.company_id)
    found = await generation_api.get(interview.generation_id, interview.company_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Generation not found")

    return found


@router.post("/{interview_id}/generation/review")
async def review_generation(interview_id: UUID, body: ReviewIn, user: CurrentUser) -> dict:
    interview = await get_interview(interview_id)
    await require_editor(user, interview.company_id)
    response = await generation_api.review(
        interview.generation_id, interview.company_id, body.model_dump()
    )
    reviewed = passed_through(response)
    await audit.record(interview.company_id, user.uid, AuditAction.TOPICS_APPROVED, interview.id)

    return reviewed


@router.post("/{interview_id}/generation/retry")
async def retry_generation(interview_id: UUID, user: CurrentUser) -> dict:
    interview = await get_interview(interview_id)
    await require_editor(user, interview.company_id)

    return passed_through(await generation_api.retry(interview.generation_id, interview.company_id))


@router.post("/{interview_id}/generation/cancel")
async def cancel_generation(interview_id: UUID, user: CurrentUser) -> dict:
    """Removes the interview too, so it isn't left without questions."""
    interview = await get_interview(interview_id)
    await require_editor(user, interview.company_id)
    cancelled = passed_through(
        await generation_api.cancel(interview.generation_id, interview.company_id)
    )
    await interviews.remove(interview.id)

    return cancelled
