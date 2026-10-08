import logging
import uuid
from datetime import UTC, datetime, timedelta

from prepza_common.analytics import track

from app.constants.events import INTERVIEW_FINISHED
from app.constants.invites import EXPIRIES_PER_BATCH, INVITE_EXPIRY_DAYS, NOT_STARTED, InviteStatus
from app.helpers.candidates import finished_result, hold_key, stored_results
from app.helpers.notifications import candidate_finished
from app.integrations import billing, rounds
from app.services import outbox as outbox_service
from app.storage import interviews, invites

logger = logging.getLogger(__name__)


async def results_of(invite_id: uuid.UUID) -> dict:
    """The candidate's results from rounds; none when rounds can't say now (the candidates list
    stores them later)."""
    try:
        scores = await rounds.invite_scores([invite_id])
    except Exception:
        logger.warning("No results for invite %s: rounds didn't answer", invite_id, exc_info=True)

        return {}

    return scores.get(str(invite_id)) or {}


async def handle(event_type: str, data: dict, event_id: str) -> None:
    """A finished interview charges the company for the candidate if they picked at least one
    answer, and tells it once, however often the event comes; one finished without an answer
    gives the credits back. Billing counts each charge or release once too. Other events aren't
    ours."""
    if event_type != INTERVIEW_FINISHED:
        return

    invite = await invites.get(uuid.UUID(data["candidate_invite_id"]))

    # Removed, or the candidate deleted their account: its credits were settled then.
    if invite is None or invite.status == InviteStatus.DELETED:
        return

    interview = await interviews.get(invite.interview_id)
    charged = data["answered"] > 0
    notice = None
    # Results from rounds when it answers; they never hold up the charge.
    grade, flagged = stored_results(await results_of(invite.id))

    # The company hears of candidates who answered something, with their grade.
    if charged:
        notice = candidate_finished(interview, invite.id, invite.email, grade)

    result = finished_result(interview, invite.id, grade, flagged)
    await invites.finish(invite.id, grade, flagged, notice, event_id, result)
    await outbox_service.flush_quietly()

    key = hold_key(invite.interview_id, invite.email, invite.hold_key)

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
    count = 0

    # Each invite's credits are released before it's marked expired: if billing fails, the
    # rest stay unexpired and the next run tries them again, so no hold is left open.
    while rows := await invites.expiring(before, EXPIRIES_PER_BATCH):
        for invite in rows:
            key = hold_key(invite.interview_id, invite.email, invite.hold_key)
            await billing.release_candidate(key)

            # Started or sent again since it was read: it keeps its credits after all.
            if not await invites.mark_expired(invite.id, before):
                await hold_again(invite, key)

        count += len(rows)

    return count


async def hold_again(invite, key: str) -> None:
    """Sets aside again the credits of an invite revived while it was expiring; the run goes on
    if billing refuses. One expired meanwhile by an overlapping run (a retried schedule), or
    removed, keeps nothing set aside."""
    try:
        current = await invites.get(invite.id)

        if current is None or current.status in (InviteStatus.EXPIRED, InviteStatus.DELETED):
            return

        interview = await interviews.get(invite.interview_id)
        await billing.hold_candidate(interview.company_id, key)
    except Exception:
        logger.warning("Couldn't hold credits again for invite %s", invite.id, exc_info=True)


async def release_unfinished(rows: list) -> None:
    """Before a candidate's invites lose their email: the ones not finished give their credits
    back."""
    for interview_id, email, status, stored in rows:
        if status in (*NOT_STARTED, InviteStatus.IN_PROCESS):
            await billing.release_candidate(hold_key(interview_id, email, stored))
