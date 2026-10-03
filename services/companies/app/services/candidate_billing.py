import uuid
from datetime import UTC, datetime, timedelta

from prepza_common.analytics import track

from app.constants.events import INTERVIEW_FINISHED
from app.constants.invites import INVITE_EXPIRY_DAYS, NOT_STARTED, InviteStatus
from app.helpers.candidates import candidate_key
from app.integrations import billing
from app.storage import interviews, invites


async def handle(event_type: str, data: dict) -> None:
    """A finished interview charges the company for the candidate if they picked at least one
    answer; one finished without an answer gives the credits back. Other events aren't ours."""
    if event_type != INTERVIEW_FINISHED:
        return

    invite = await invites.get(uuid.UUID(data["candidate_invite_id"]))

    # Removed, or the candidate deleted their account: its credits were settled then.
    if invite is None or invite.status == InviteStatus.DELETED:
        return

    if invite.status != InviteStatus.FINISHED:
        await invites.set_status([invite.id], InviteStatus.FINISHED)

    key = candidate_key(invite.interview_id, invite.email)

    charged = data["answered"] > 0

    if charged:
        await billing.charge_candidate(key)
    else:
        await billing.release_candidate(key)

    interview = await interviews.get(invite.interview_id)
    await track(
        "interview_finished",
        company_id=interview.company_id if interview else None,
        answered=data["answered"],
        charged=charged,
    )


async def expire_unstarted() -> int:
    """Daily: invites never started within INVITE_EXPIRY_DAYS of being sent expire, and their
    credits come back."""
    before = datetime.now(UTC) - timedelta(days=INVITE_EXPIRY_DAYS)
    expired = await invites.expire_unstarted(before)

    for invite in expired:
        await billing.release_candidate(candidate_key(invite.interview_id, invite.email))

    return len(expired)


async def release_unfinished(rows: list) -> None:
    """Before a candidate's invites lose their email: the ones not finished give their credits
    back."""
    for interview_id, email, status in rows:
        if status in (*NOT_STARTED, InviteStatus.IN_PROCESS):
            await billing.release_candidate(candidate_key(interview_id, email))
