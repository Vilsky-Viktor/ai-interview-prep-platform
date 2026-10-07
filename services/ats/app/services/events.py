import logging
from uuid import UUID

from app.constants.events import (
    CANDIDATE_FINISHED,
    COMPANY_DELETED,
    COMPANY_OWNER,
    CREDITS_ADDED,
    INTERVIEW_DELETED,
    INTERVIEW_READY,
)
from app.services import ats_candidates
from app.storage import ats

logger = logging.getLogger(__name__)


async def handle(event_type: str, data: dict) -> None:
    """Companies' and billing's events. Each is safe to run again on a redelivery: a report goes
    back once (reported_at), a candidate is invited once (the claim), and deleting twice deletes
    nothing more. Other events are ignored."""
    if event_type == CANDIDATE_FINISHED:
        await ats_candidates.report(data)
    elif event_type == INTERVIEW_READY:
        await ats_candidates.invite_waiting(UUID(data["interview_id"]))
    elif event_type == INTERVIEW_DELETED:
        await ats.delete_interview(UUID(data["interview_id"]))
    elif event_type == COMPANY_DELETED:
        await ats.delete_company(UUID(data["company_id"]))
    elif event_type == CREDITS_ADDED and data.get("owner_type") == COMPANY_OWNER:
        try:
            company_id = UUID(str(data.get("owner_id")))
        except ValueError:
            # Retrying can't fix it: dropped, so Pub/Sub doesn't send it again and again.
            logger.warning("Dropped credits.added for a malformed owner %r", data.get("owner_id"))

            return

        await ats_candidates.topped_up(company_id)
