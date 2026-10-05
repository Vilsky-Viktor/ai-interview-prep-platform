from prepza_common.analytics import track
from prepza_common.rate_limit import hit_emails
from prepza_common.user import User

from app.config.settings import settings
from app.constants.invites import NOT_STARTED
from app.helpers.candidates import candidate_key
from app.helpers.interviews import interview_title
from app.helpers.logos import logo_path
from app.integrations import billing
from app.integrations.redis import get_redis
from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage import invites


async def invite(interview: Interview, company: Company, user: User, email: str) -> CandidateInvite:
    """Invites one candidate, or sends their invite again, with the invite email queued. Raises
    429 over the member's email limits and billing's 402 when the company is out of credits."""
    email = email.lower()

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
        invite = await invites.upsert(
            interview.id, email, title, company.name, interview.language, logo_path(company)
        )
    except Exception:
        # A brand-new invite that couldn't be saved gives its credits back.
        if current is None:
            await billing.release_candidate(key)

        raise

    if current is None:
        await track("candidate_invited", user_id=user.uid, company_id=company.id)

    return invite
