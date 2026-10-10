from fastapi import HTTPException
from prepza_common.analytics import track
from prepza_common.names import clean_name
from prepza_common.rate_limit import hit_emails
from prepza_common.user import User

from app.config.settings import settings
from app.constants.invites import NOT_STARTED, InviteStatus
from app.helpers.candidates import new_hold_key
from app.helpers.interviews import interview_title
from app.helpers.logos import logo_path
from app.integrations import billing
from app.integrations.redis import get_redis
from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services.candidate_billing import hold_again
from app.storage import invites


async def invite(
    interview: Interview, company: Company, user: User, email: str, name: str | None = None
) -> CandidateInvite:
    """Invites one candidate, or sends their invite again, with the invite email queued; `name`
    (untrusted: cleaned here) fills their name if it isn't known yet. Raises 429 over the
    member's email limits and billing's 402 when the company is out of credits."""
    email = email.lower()

    current, stored = await invites.held(interview.id, email)
    key = stored if current else new_hold_key(interview.id)

    # A candidate who hasn't started has credits set aside: new, or sent again after expiring.
    # Credits first, so an invite refused for them never uses up the email limits.
    if current is None or current in NOT_STARTED:
        await billing.hold_candidate(company.id, key)

    try:
        await hit_emails(
            get_redis(),
            user.uid,
            f"{interview.id}:{email}",
            settings.email_hourly_limit,
            settings.email_daily_limit,
            settings.email_recipient_daily_limit,
        )
    except HTTPException:
        await give_back(interview, company, email, current, key)

        raise

    title = await interview_title(interview) or "an interview"

    try:
        invite, revived = await invites.upsert(
            interview.id,
            email,
            title,
            company.name,
            interview.language,
            logo_path(company),
            hold_key=key,
            name=clean_name(name),
        )
    except Exception:
        # A brand-new invite that couldn't be saved gives its credits back.
        if current is None:
            await billing.release_candidate(key)

        raise

    # Invited at the same moment by another request, whose own key and credits were kept.
    if current is None and invite.hold_key != key:
        await billing.release_candidate(key)

    # Expired after it was read here: expiry gave its credits back.
    if revived:
        await hold_again(invite, key)

    if current is None:
        await track("candidate_invited", user_id=user.uid, company_id=company.id)

    return invite


async def give_back(interview: Interview, company: Company, email: str, current, key: str) -> None:
    """An invite refused over the email limits gives back the credits set aside for it just now:
    a new one's, or an expired one's (expiry had given them back). One already invited keeps
    its own. An expired invite sent again by another request meanwhile keeps them after all."""
    if current is not None and current != InviteStatus.EXPIRED:
        return

    await billing.release_candidate(key)

    if current == InviteStatus.EXPIRED and await invites.status_of(interview.id, email) not in (
        InviteStatus.EXPIRED,
        InviteStatus.DELETED,
    ):
        await billing.hold_candidate(company.id, key)
