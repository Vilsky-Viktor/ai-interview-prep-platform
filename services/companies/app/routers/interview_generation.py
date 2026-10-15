from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.auth import CurrentUser
from prepza_common.http import passed_on
from prepza_common.human_check import require_human
from prepza_common.pause import refuse_if_paused

from app.config.settings import settings
from app.constants.audit import AuditAction
from app.constants.generation import GENERATION_REFUSALS
from app.integrations import billing
from app.integrations import generation as generation_api
from app.integrations.redis import get_redis
from app.models.interviews import Interview
from app.schemas.generations import GenerationOut
from app.schemas.interviews import ReviewIn
from app.service_auth import Via
from app.services.interview_access import interview_for
from app.storage import audit, interview_generations, interviews

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def get_interview(user: CurrentUser, interview_id: UUID, editor: bool = False) -> Interview:
    """The user's interview (interview_for), only one with a generation to follow."""
    interview, _, _ = await interview_for(user, interview_id, editor)

    # A test made from a template has no generation to follow.
    if interview.generation_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    return interview


@router.get("/{interview_id}/generation")
async def get_generation(interview_id: UUID, user: CurrentUser) -> GenerationOut:
    """Every company member follows the generation, not only the admin who started it."""
    interview = await get_interview(user, interview_id)
    found = await generation_api.get(interview.generation_id, interview.company_id)

    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Generation not found")

    return found


@router.post("/{interview_id}/generation/review")
async def review_generation(
    interview_id: UUID, body: ReviewIn, user: CurrentUser, via: Via, request: Request
) -> dict:
    """Approved topics resume the generation, so a pause refuses it. A company that never paid
    shows it's a person on the site first, as generating costs; the assistant and AI apps (no
    browser) can't be asked."""
    await refuse_if_paused(get_redis())
    interview = await get_interview(user, interview_id, editor=True)

    if (
        via is None
        and settings.turnstile_secret_key
        and not await billing.company_paid(interview.company_id)
    ):
        await require_human(request, settings.turnstile_secret_key)

    response = await generation_api.review(
        interview.generation_id, interview.company_id, body.model_dump()
    )
    reviewed = passed_on(response, GENERATION_REFUSALS).json()
    await audit.record(
        interview.company_id, user.uid, AuditAction.TOPICS_APPROVED, interview.id, via=via
    )

    return reviewed


@router.post("/{interview_id}/generation/retry")
async def retry_generation(interview_id: UUID, user: CurrentUser) -> dict:
    await refuse_if_paused(get_redis())
    interview = await get_interview(user, interview_id, editor=True)
    retried = passed_on(
        await generation_api.retry(interview.generation_id, interview.company_id),
        GENERATION_REFUSALS,
    ).json()
    # Generating again: its lists stop showing the failure.
    await interview_generations.set_generation_failed(interview.id, False)

    return retried


@router.post("/{interview_id}/generation/cancel")
async def cancel_generation(interview_id: UUID, user: CurrentUser) -> dict:
    """Removes the interview too, so it isn't left without questions."""
    interview = await get_interview(user, interview_id, editor=True)
    cancelled = passed_on(
        await generation_api.cancel(interview.generation_id, interview.company_id),
        GENERATION_REFUSALS,
    ).json()
    await interviews.remove(interview.id)

    return cancelled
