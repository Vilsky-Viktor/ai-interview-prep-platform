import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.config.settings import settings
from app.constants.assistant import RETENTION_BATCH
from app.constants.mcp import IDLE_CLIENT_DAYS
from app.storage import conversations, oauth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/retention", status_code=status.HTTP_204_NO_CONTENT)
async def retention() -> None:
    """Daily, from Cloud Scheduler: conversations nobody added to for ASSISTANT_RETENTION_DAYS
    go, with their messages and tool calls, a batch at a time until none are left; so do AI
    apps' connections whose refresh token expired, and apps with no connection that registered
    over IDLE_CLIENT_DAYS ago. Safe to run twice at once or again: each deletes what's still
    there."""
    now = datetime.now(UTC)
    grants, clients = await oauth.delete_expired(now, now - timedelta(days=IDLE_CLIENT_DAYS))

    if grants or clients:
        logger.info("Deleted %d expired AI app connections and %d idle apps", grants, clients)

    before = now - timedelta(days=settings.assistant_retention_days)
    deleted = 0

    while True:
        batch = await conversations.delete_idle(before, RETENTION_BATCH)
        deleted += batch

        if batch < RETENTION_BATCH:
            break

    if deleted:
        logger.info("Deleted %d assistant conversations past their retention", deleted)
