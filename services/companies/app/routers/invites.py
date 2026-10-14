from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser, OptionalUser
from prepza_common.pause import refuse_if_paused

from app.constants.invites import EMAIL_NOT_VERIFIED, NOT_THE_GUEST, InviteStatus
from app.helpers.candidates import candidate_seconds
from app.helpers.interviews import attach_set, interview_title
from app.helpers.logos import logo_path
from app.integrations.firebase_tokens import guest_token, guest_uid
from app.integrations.redis import get_redis
from app.schemas.invites import GuestTokenOut, InviteStartOut, InviteView
from app.services.access import refuse_if_suspended
from app.services.candidate_start import start_sessions
from app.storage import companies
from app.storage import invites as invite_store

router = APIRouter(prefix="/invites", tags=["invites"])


@router.get("/{token}")
async def get_invite(token: str, user: OptionalUser) -> InviteView:
    """The invitation, also before signing in, so the page shows what it's for; the candidate's
    email only once someone is signed in."""
    found = await invite_store.get_by_token(token)

    # An expired invite's link stops working until the company sends it again.
    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found
    interview = await attach_set(interview)
    title = await interview_title(interview)

    company = await companies.get(interview.company_id)
    refuse_if_suspended(company, invite.status)

    return InviteView(
        interview_id=interview.id,
        title=title,
        company=company.name if company else "",
        logo_url=logo_path(company),
        verified_domain=company.verified_domain if company else None,
        email=invite.email if user else None,
        status=invite.status,
        question_seconds=candidate_seconds(interview.question_seconds, invite.extra_time),
        guest=invite.guest,
        embed_domain=company.website_domain if company and invite.guest else None,
    )


@router.post("/{token}/guest")
async def sign_in_guest(token: str) -> GuestTokenOut:
    """A sign-in for the candidate a company's own platform sent: the link is all they need."""
    found = await invite_store.get_by_token(token)

    if found is None or found[0].status == InviteStatus.EXPIRED or not found[0].guest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    return GuestTokenOut(token=await guest_token(found[0].id))


@router.post("/{token}/start")
async def start_invite(token: str, user: CurrentUser) -> InviteStartOut:
    """Only the invited, verified email can start, so a forwarded link is useless to anyone else;
    a guest invite, only its guest (its link signs them in)."""
    found = await invite_store.get_by_token(token)

    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found

    if invite.guest:
        if user.uid != guest_uid(invite.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, NOT_THE_GUEST)
    elif not user.email_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, EMAIL_NOT_VERIFIED)
    elif user.email.lower() != invite.email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    if invite.status == InviteStatus.FINISHED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This interview is already finished")

    refuse_if_suspended(await companies.get(interview.company_id), invite.status)

    # Paused, nobody starts; a candidate already in the interview may finish it.
    if invite.status != InviteStatus.IN_PROCESS:
        await refuse_if_paused(get_redis())

    return await start_sessions(invite, interview, user)
