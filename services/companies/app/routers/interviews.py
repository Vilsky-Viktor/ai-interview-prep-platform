from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.constants import DAY_SECONDS
from prepza_common.paging import PageParams
from prepza_common.rate_limit import hit, hit_emails

from app.config.settings import settings
from app.constants.invites import (
    INTERVIEWS_PER_DAY,
    NOT_STARTED,
    TOO_MANY_INTERVIEWS,
    InviteStatus,
)
from app.constants.roles import Role
from app.helpers.candidates import candidate_key
from app.helpers.interviews import (
    attach_set,
    interview_out,
    interview_title,
    topics_out,
)
from app.integrations import billing, library, rounds
from app.integrations import generation as generation_api
from app.integrations.redis import get_redis
from app.schemas.interviews import (
    InterviewCreate,
    InterviewDetail,
    InterviewOut,
    InterviewSettings,
    TitleIn,
)
from app.schemas.invites import CandidateIn, CandidateOut
from app.services import outbox as outbox_service
from app.services.access import require_company, require_manager
from app.services.candidate_billing import release_unfinished
from app.storage import interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_interview(
    body: InterviewCreate, company_id: UUID, user: CurrentUser
) -> InterviewOut:
    company, _ = await require_company(user, company_id)

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
        created = await generation_api.create(body.text, company.id, user.uid, user.language)
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


@router.post("/{interview_id}/candidates", status_code=status.HTTP_201_CREATED)
async def invite_candidate(
    interview_id: UUID, body: CandidateIn, user: CurrentUser
) -> CandidateOut:
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    company, _ = await require_company(user, interview.company_id)

    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is still being generated")

    email = str(body.email).lower()

    # Email limits first, so a refused invite never leaves credits set aside.
    await hit_emails(
        get_redis(),
        user.uid,
        f"{interview.id}:{email}",
        settings.email_hourly_limit,
        settings.email_daily_limit,
        settings.email_recipient_daily_limit,
    )
    current = await invites.status_of(interview.id, email)
    key = candidate_key(interview.id, email)
    # A candidate who hasn't started has credits set aside: new, or sent again after expiring.
    if current is None or current in NOT_STARTED:
        await billing.hold_candidate(company.id, key)

    title = await interview_title(interview) or "an interview"

    try:
        invite = await invites.upsert(interview.id, email, title, company.name, interview.language)
    except Exception:
        # A brand-new invite that couldn't be saved gives its credits back.
        if current is None:
            await billing.release_candidate(key)

        raise

    await outbox_service.flush_quietly()

    if current is None:
        await track("candidate_invited", user_id=user.uid, company_id=company.id)

    return CandidateOut(
        id=invite.id, email=invite.email, status=invite.status, created_at=invite.created_at
    )


@router.get("/{interview_id}/candidates")
async def list_candidates(
    interview_id: UUID, user: CurrentUser, page: PageParams
) -> list[CandidateOut]:
    """Newest first, a page at a time; scores come from rounds for this page only."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_company(user, interview.company_id)
    listed = await invites.list_for_interview(interview.id, page.offset, page.limit)
    totals = await rounds.invite_scores([invite.id for invite in listed])
    finished = [
        invite.id
        for invite in listed
        if (totals.get(str(invite.id)) or {}).get("finished")
        and invite.status != InviteStatus.FINISHED
    ]

    if finished:
        await invites.set_status(finished, InviteStatus.FINISHED)

        for invite in listed:
            if invite.id in finished:
                invite.status = InviteStatus.FINISHED

    return [
        CandidateOut(
            id=invite.id,
            email=invite.email,
            status=invite.status,
            progress=(totals.get(str(invite.id)) or {}).get("progress", 0),
            grade=(totals.get(str(invite.id)) or {}).get("grade"),
            created_at=invite.created_at,
        )
        for invite in listed
    ]


@router.delete("/{interview_id}/candidates/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_candidate(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> None:
    """Withdraws an invite the candidate hasn't used yet; later it would discard their answers."""
    interview = await interviews.get(interview_id)
    invite = next(
        (item for item in (interview.invites if interview else []) if item.id == invite_id), None
    )

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_company(user, interview.company_id)

    if invite.status not in NOT_STARTED:
        raise HTTPException(status.HTTP_409_CONFLICT, "The candidate has already started")

    await billing.release_candidate(candidate_key(interview.id, invite.email))
    await invites.remove(invite.id)


@router.get("/{interview_id}/candidates/{invite_id}")
async def candidate_scorecard(interview_id: UUID, invite_id: UUID, user: CurrentUser) -> dict:
    interview = await interviews.get(interview_id)
    invite = next(
        (item for item in (interview.invites if interview else []) if item.id == invite_id), None
    )

    if interview is None or invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    await require_company(user, interview.company_id)

    card = await rounds.scorecard(invite.id) or []

    finished = card and all(item["status"] == "finished" for item in card)

    if finished and invite.status != InviteStatus.FINISHED:
        await invites.set_status([invite.id], InviteStatus.FINISHED)
        invite.status = InviteStatus.FINISHED

    return {
        "id": str(invite.id),
        "email": invite.email,
        "status": invite.status,
        "sessions": card,
    }
