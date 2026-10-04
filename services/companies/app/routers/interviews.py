from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.constants import DAY_SECONDS
from prepza_common.paging import PageParams
from prepza_common.rate_limit import hit

from app.constants.invites import (
    INTERVIEWS_PER_DAY,
    MAX_INTERVIEWS_WITHOUT_CANDIDATES,
    TOO_MANY_INTERVIEWS,
    TOO_MANY_WITHOUT_CANDIDATES,
)
from app.constants.roles import Role
from app.helpers.interviews import (
    attach_set,
    interview_out,
    topics_out,
)
from app.integrations import generation as generation_api
from app.integrations import library, rounds
from app.integrations.redis import get_redis
from app.schemas.interviews import (
    InterviewCreate,
    InterviewDetail,
    InterviewOut,
    InterviewSettings,
    TitleIn,
)
from app.services.access import require_company, require_manager
from app.services.candidate_billing import release_unfinished
from app.storage import interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_interview(
    body: InterviewCreate, company_id: UUID, user: CurrentUser
) -> InterviewOut:
    company, _ = await require_company(user, company_id)

    # Checked first, so a refused attempt doesn't count towards the day's limit.
    if await interviews.without_candidates(company.id) >= MAX_INTERVIEWS_WITHOUT_CANDIDATES:
        await track(
            "limit_hit",
            user_id=user.uid,
            company_id=company.id,
            which="interviews_without_candidates",
        )

        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, TOO_MANY_WITHOUT_CANDIDATES)

    try:
        await hit(
            get_redis(),
            f"rate:interviews:{company.id}",
            INTERVIEWS_PER_DAY,
            DAY_SECONDS,
            TOO_MANY_INTERVIEWS,
        )
    except HTTPException:
        await track("limit_hit", user_id=user.uid, company_id=company.id, which="interviews_a_day")
        raise

    try:
        created = await generation_api.create(
            body.text, company.id, user.uid, user.language, body.generate_in
        )
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests. Try again later."
            )

        raise

    # Generation picks the language from the job description, not from the recruiter's interface.
    interview = await interviews.create(company.id, created["id"], created["language"])

    return await interview_out(interview)


@router.get("")
async def list_interviews(
    company_id: UUID, user: CurrentUser, page: PageParams
) -> list[InterviewOut]:
    company, _ = await require_company(user, company_id)
    rows = await interviews.list_for_company(company.id, page.offset, page.limit)

    return [await interview_out(item) for item in rows]


@router.get("/{interview_id}")
async def get_interview(interview_id: UUID, user: CurrentUser) -> InterviewDetail:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)

    base = await interview_out(interview)
    found = await library.get_set(interview.set_id) if interview.set_id else None

    topics = topics_out(found, interview.topic_limits) if found else []

    return InterviewDetail(**base.model_dump(), topics=topics)


@router.patch("/{interview_id}/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_settings(interview_id: UUID, body: InterviewSettings, user: CurrentUser) -> None:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    _, member = await require_company(user, interview.company_id)

    if member.role not in (Role.OWNER, Role.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't change this interview")

    await interviews.update_settings(interview.id, body)


@router.patch("/{interview_id}/title", status_code=status.HTTP_204_NO_CONTENT)
async def rename_interview(interview_id: UUID, body: TitleIn, user: CurrentUser) -> None:
    """Company owners and admins can rename an interview once it has been generated."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    _, member = await require_company(user, interview.company_id)

    if member.role not in (Role.OWNER, Role.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't rename this interview")

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    await library.rename_set(interview.set_id, body.title)
    await interviews.set_title(interview.id, body.title)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(interview_id: UUID, user: CurrentUser) -> None:
    """Results and questions go first, so a failure leaves the interview to delete again."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_manager(user, interview)
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cancel the generation instead")

    await rounds.delete_interview_data(interview.set_id)
    await library.delete_interview(interview.set_id)
    await release_unfinished(await invites.unfinished(interview.id))
    await interviews.remove(interview.id)
