import logging
import uuid
from datetime import UTC, datetime, timedelta

from prepza_common.analytics import track

from app.constants.events import INTERVIEW_FINISHED
from app.constants.invites import INVITE_EXPIRY_DAYS, NOT_STARTED, InviteStatus
from app.helpers.candidates import candidate_key
from app.helpers.notifications import candidate_finished
from app.integrations import billing, rounds
from app.services import outbox as outbox_service
from app.storage import interviews, invites

logger = logging.getLogger(__name__)


async def grade_of(invite_id: uuid.UUID) -> int | None:
    """The candidate's grade for the company's notification; none when rounds can't say now."""
    try:
        scores = await rounds.invite_scores([invite_id])
    except Exception:
        logger.warning("No grade for invite %s: rounds didn't answer", invite_id, exc_info=True)

        return None

    return (scores.get(str(invite_id)) or {}).get("grade")


async def handle(event_type: str, data: dict) -> None:
    """A finished interview charges the company for the candidate if they picked at least one
    answer, and tells it; one finished without an answer gives the credits back. Other events
    aren't ours."""
    if event_type != INTERVIEW_FINISHED:
        return

    invite = await invites.get(uuid.UUID(data["candidate_invite_id"]))

    # Removed, or the candidate deleted their account: its credits were settled then.
    if invite is None or invite.status == InviteStatus.DELETED:
        return

    interview = await interviews.get(invite.interview_id)
    charged = data["answered"] > 0
    notice = None

    # The company hears of candidates who answered something, with their grade from rounds when
    # it answers; the notification never holds up the charge.
    if charged:
        notice = candidate_finished(interview, invite.id, invite.email, await grade_of(invite.id))

    await invites.finish(invite.id, notice)
    await outbox_service.flush_quietly()

    key = candidate_key(invite.interview_id, invite.email)

    if charged:
        await billing.charge_candidate(key)
    else:
        await billing.release_candidate(key)

    await track(
        "interview_finished",
        company_id=interview.company_id,
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
