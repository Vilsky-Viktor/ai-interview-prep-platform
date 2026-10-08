import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.config.settings import settings
from app.constants.assistant import RETENTION_BATCH
from app.storage import conversations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/retention", status_code=status.HTTP_204_NO_CONTENT)
async def retention() -> None:
    """Daily, from Cloud Scheduler: conversations nobody added to for ASSISTANT_RETENTION_DAYS
    go, with their messages and tool calls, a batch at a time until none are left. Safe to run
    twice at once or again: each batch deletes what's still there."""
    before = datetime.now(UTC) - timedelta(days=settings.assistant_retention_days)
    deleted = 0

    while True:
        batch = await conversations.delete_idle(before, RETENTION_BATCH)
        deleted += batch

        if batch < RETENTION_BATCH:
            break

    if deleted:
        logger.info("Deleted %d assistant conversations past their retention", deleted)
