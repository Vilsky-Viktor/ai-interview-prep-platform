from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.constants import MAX_PAGE_SIZE
from prepza_common.pause import refuse_if_paused
from prepza_common.user import User
from pydantic import EmailStr

from app.constants.audit import VIA_API
from app.constants.invites import NO_EMAILS_FOR_GUEST, InviteStatus
from app.integrations.redis import get_redis
from app.routers.internal_api import company_interview
from app.schemas.companies import CompanyCreditsOut
from app.schemas.interviews import InterviewCreate, InterviewOut
from app.schemas.invites import CandidateNameIn, ExtraTimeIn, FoundCandidateOut
from app.service_auth import ServiceCaller
from app.services import candidate_changes, candidate_invites, credits, interview_creation
from app.services import outbox as outbox_service
from app.storage import candidates, companies

# What an API key changes, as `user_id`, the owner or admin who made it (the api service
# checked they still are), and finds by email.
router = APIRouter(prefix="/internal/companies/{company_id}", tags=["internal"])


async def company_candidate(company_id: UUID, interview_id: UUID, invite_id: UUID):
    interview = await company_interview(company_id, interview_id)
    invite = await candidates.get(interview.id, invite_id)

    if invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    return interview, invite


@router.post("/interviews", status_code=status.HTTP_201_CREATED)
async def create_interview(
    company_id: UUID, body: InterviewCreate, user_id: str, caller: ServiceCaller
) -> InterviewOut:
    await refuse_if_paused(get_redis())
    company = await companies.get(company_id)

    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    return await interview_creation.create(company, user_id, None, body.text, body.generate_in)


@router.delete(
    "/interviews/{interview_id}/candidates/{invite_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_candidate(
    company_id: UUID, interview_id: UUID, invite_id: UUID, user_id: str, caller: ServiceCaller
) -> None:
    interview, invite = await company_candidate(company_id, interview_id, invite_id)
    await candidate_changes.remove(interview, invite, user_id, VIA_API)


@router.patch(
    "/interviews/{interview_id}/candidates/{invite_id}/name",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def rename_candidate(
    company_id: UUID,
    interview_id: UUID,
    invite_id: UUID,
    body: CandidateNameIn,
    caller: ServiceCaller,
) -> None:
    _, invite = await company_candidate(company_id, interview_id, invite_id)
    await candidate_changes.rename(invite, body.name)


@router.put(
    "/interviews/{interview_id}/candidates/{invite_id}/extra-time",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def set_extra_time(
    company_id: UUID,
    interview_id: UUID,
    invite_id: UUID,
    body: ExtraTimeIn,
    user_id: str,
    caller: ServiceCaller,
) -> None:
    interview, invite = await company_candidate(company_id, interview_id, invite_id)
    await candidate_changes.set_extra_time(interview, invite, body.extra_time, user_id, VIA_API)


@router.post(
    "/interviews/{interview_id}/candidates/{invite_id}/resend",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def resend_invite(
    company_id: UUID, interview_id: UUID, invite_id: UUID, user_id: str, caller: ServiceCaller
) -> None:
    """Sends the invite again, as an owner or admin does on the candidate's page: refused for a
    candidate who finished (409) or one prepza doesn't email (invited without a sign-in, 409);
    the invite keeps its return address and theme."""
    interview, invite = await company_candidate(company_id, interview_id, invite_id)

    if invite.status == InviteStatus.DELETED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    if invite.guest:
        raise HTTPException(status.HTTP_409_CONFLICT, NO_EMAILS_FOR_GUEST)

    company = await companies.get(company_id)
    sender = User(uid=user_id, email="", email_verified=True)
    await candidate_invites.invite(interview, company, sender, invite.email)
    await outbox_service.flush_quietly()


@router.get("/candidates")
async def find_candidates(
    company_id: UUID, email: EmailStr, caller: ServiceCaller
) -> list[FoundCandidateOut]:
    """The company's candidates invited with this email, in any of its interviews, newest
    first."""
    rows = await candidates.company_page(company_id, 0, MAX_PAGE_SIZE, email=str(email))

    return [
        FoundCandidateOut(interview_id=interview.id, candidate_id=invite.id)
        for invite, interview in rows
    ]


@router.get("/credits")
async def get_credits(company_id: UUID, caller: ServiceCaller) -> CompanyCreditsOut:
    return await credits.credits_of(company_id)
