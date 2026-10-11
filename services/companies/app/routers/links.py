import secrets
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser, OptionalUser
from prepza_common.client_ip import client_ip
from prepza_common.constants import HOUR_SECONDS
from prepza_common.pause import refuse_if_paused
from prepza_common.rate_limit import hit

from app.constants.invites import (
    LINK_CLOSED,
    LINK_STARTS_PER_HOUR,
    LINK_STARTS_PER_IP_HOUR,
    LINK_TOKEN_BYTES,
    NOT_STARTED,
    InviteStatus,
)
from app.helpers.candidates import new_hold_key
from app.helpers.interviews import attach_set, interview_title
from app.helpers.logos import logo_path
from app.integrations import billing
from app.integrations.redis import get_redis
from app.schemas.invites import InviteStartOut, LinkIn, LinkOut, LinkView
from app.services.access import require_editor
from app.services.candidate_start import start_sessions
from app.storage import companies, interviews, invites

# One link for many candidates: a company puts it in a job ad, and each person who opens it
# takes the test as an invited candidate would.
router = APIRouter(tags=["links"])


async def linked_interview(token: str):
    interview = await interviews.get_by_link(token)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")

    return interview


@router.put("/interviews/{interview_id}/link")
async def set_link(interview_id: UUID, body: LinkIn, user: CurrentUser) -> LinkOut:
    """Owners and admins turn the link on (a new code) or off (it stops working at once)."""
    interview = await interviews.get(interview_id)

    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    await require_editor(user, interview.company_id)
    token = (interview.link_token or secrets.token_urlsafe(LINK_TOKEN_BYTES)) if body.on else None
    await interviews.set_link(interview.id, token)

    return LinkOut(link_token=token)


@router.get("/links/{token}")
async def get_link(token: str, user: OptionalUser) -> LinkView:
    """Shown to anyone with the link, signed in or not, before they start. Signed in, it also
    says how far they got, so a finished test is never offered again."""
    interview = await attach_set(await linked_interview(token))
    company = await companies.get(interview.company_id)

    return LinkView(
        title=await interview_title(interview),
        company=company.name if company else "",
        logo_url=logo_path(company),
        verified_domain=company.verified_domain if company else None,
        question_seconds=interview.question_seconds,
        status=await invites.status_of(interview.id, user.email) if user else None,
    )


@router.post("/links/{token}/start")
async def start_link(token: str, user: CurrentUser, request: Request) -> InviteStartOut:
    """The signed-in person becomes a candidate (their verified email, one attempt each) and
    starts, with credits set aside as for an email invite."""
    interview = await linked_interview(token)

    if not user.email_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sign in with a verified email")

    current, stored = await invites.held(interview.id, user.email)
    key = stored if current else new_hold_key(interview.id)

    if current == InviteStatus.FINISHED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This interview is already finished")

    # Paused, nobody starts; a candidate already in the interview may finish it.
    if current != InviteStatus.IN_PROCESS:
        await refuse_if_paused(get_redis())

    # A new candidate counts toward the link's and their address's hourly limits; one already
    # invited is never held back by them.
    if current is None:
        redis = get_redis()
        await hit(redis, f"rate:link-starts:{interview.id}", LINK_STARTS_PER_HOUR, HOUR_SECONDS)
        address = client_ip(request)
        await hit(redis, f"rate:link-starts:ip:{address}", LINK_STARTS_PER_IP_HOUR, HOUR_SECONDS)

    # Credits set aside just now: a new candidate's, or an expired invite's (expiry gave them
    # back, and won't again). Anything failing before the candidate has started gives them back.
    fresh = current is None or current == InviteStatus.EXPIRED

    if current is None or current in NOT_STARTED:
        try:
            await billing.hold_candidate(interview.company_id, key)
        except HTTPException as error:
            if error.status_code == status.HTTP_402_PAYMENT_REQUIRED:
                raise HTTPException(status.HTTP_409_CONFLICT, LINK_CLOSED) from error

            raise
        except Exception:
            # Billing's answer lost on the way: a hold made just now may exist. An invite's
            # earlier hold stays.
            if fresh:
                await billing.release_candidate(key)

            raise

    try:
        invite = await invites.for_link(interview.id, user.email, hold_key=key)
    except Exception:
        # An invite that couldn't be saved (its interview deleted meanwhile) gives its credits
        # back.
        if fresh:
            await billing.release_candidate(key)

        raise

    # Started at the same moment by another request, whose own key and credits were kept.
    if current is None and invite.hold_key != key:
        await billing.release_candidate(key)

    if current is None:
        await track("candidate_joined_by_link", company_id=interview.company_id)

    try:
        return await start_sessions(invite, interview, user)
    except Exception:
        # An expired invite that didn't start stays expired, and expiry won't give its credits
        # back: they go back now. A new one waits, unstarted, until it expires.
        if current == InviteStatus.EXPIRED:
            await billing.release_candidate(key)

        raise
