from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.invites import InviteStatus
from app.helpers.interviews import attach_set, interview_title
from app.helpers.logos import logo_path
from app.schemas.invites import InviteStartOut, InviteView
from app.services.candidate_start import start_sessions
from app.storage import companies
from app.storage import invites as invite_store

router = APIRouter(prefix="/invites", tags=["invites"])


@router.get("/{token}")
async def get_invite(token: str, user: CurrentUser) -> InviteView:
    found = await invite_store.get_by_token(token)

    # An expired invite's link stops working until the company sends it again.
    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found
    interview = await attach_set(interview)
    title = await interview_title(interview)

    company = await companies.get(interview.company_id)

    return InviteView(
        interview_id=interview.id,
        title=title,
        company=company.name if company else "",
        logo_url=logo_path(company),
        verified_domain=company.verified_domain if company else None,
        email=invite.email,
        status=invite.status,
        question_seconds=interview.question_seconds,
    )


@router.post("/{token}/start")
async def start_invite(token: str, user: CurrentUser) -> InviteStartOut:
    """Only the invited, verified email can start; a forwarded link is useless to anyone else."""
    found = await invite_store.get_by_token(token)

    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found

    if not user.email_verified or user.email.lower() != invite.email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    if invite.status == InviteStatus.FINISHED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This interview is already finished")

    return await start_sessions(invite, interview, user.uid)
