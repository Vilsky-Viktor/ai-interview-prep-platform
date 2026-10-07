from uuid import UUID

from app.constants.events import (
    CANDIDATE_FINISHED,
    COMPANY_DELETED,
    INTERVIEW_DELETED,
    INTERVIEW_READY,
)
from app.services import ats_candidates
from app.storage import ats


async def handle(event_type: str, data: dict) -> None:
    """Companies' events. Each is safe to run again on a redelivery: a report goes back once
    (reported_at), a candidate is invited once (the claim), and deleting twice deletes
    nothing more. Other events are ignored."""
    if event_type == CANDIDATE_FINISHED:
        await ats_candidates.report(data)
    elif event_type == INTERVIEW_READY:
        await ats_candidates.invite_waiting(UUID(data["interview_id"]))
    elif event_type == INTERVIEW_DELETED:
        await ats.delete_interview(UUID(data["interview_id"]))
    elif event_type == COMPANY_DELETED:
        await ats.delete_company(UUID(data["company_id"]))
