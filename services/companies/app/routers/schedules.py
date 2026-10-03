import logging

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.services import outbox as outbox_service
from app.services.candidate_billing import expire_unstarted
from app.services.retention import delete_expired_candidates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/retention", status_code=status.HTTP_204_NO_CONTENT)
async def retention() -> None:
    """Daily, from Cloud Scheduler: candidate data past its retention period goes."""
    count = await delete_expired_candidates()

    if count:
        logger.info("Deleted %d expired candidate invites", count)


@router.post("/invite-expiry", status_code=status.HTTP_204_NO_CONTENT)
async def invite_expiry() -> None:
    """Daily, from Cloud Scheduler: invites never started expire, and their credits come back."""
    count = await expire_unstarted()

    if count:
        logger.info("Expired %d invites never started", count)


@router.post("/outbox", status_code=status.HTTP_204_NO_CONTENT)
async def flush_outbox() -> None:
    """Every minute, from Cloud Scheduler: publishes events that weren't published right after
    their change."""
    await outbox_service.flush()
