import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.constants.member_emails import SENT_KEEP_DAYS
from app.integrations.resend import ResendBusy
from app.services.digest import send_digests
from app.services.reminders import send_reminders
from app.storage import sent_emails

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/digest", status_code=status.HTTP_204_NO_CONTENT)
async def digest() -> None:
    """Every 10 minutes for an hour each morning, from Cloud Scheduler: the activity digest. Each
    run goes on where the last one stopped; nobody gets it twice in a day."""
    await run("digests", send_digests)


@router.post("/reminders", status_code=status.HTTP_204_NO_CONTENT)
async def reminders() -> None:
    """Every 10 minutes for an hour each morning, from Cloud Scheduler: reminders, each kind
    at most once a week to a user. The sent log's old rows go too."""
    await run("reminders", send_reminders)
    await sent_emails.forget(datetime.now(UTC).date() - timedelta(days=SENT_KEEP_DAYS))


async def run(name: str, send) -> None:
    """Over Resend's per-second limit the run stops quietly: the next one goes on."""
    try:
        count = await send(datetime.now(UTC))
    except ResendBusy:
        logger.warning("Resend is busy: the next run sends the remaining %s", name)

        return

    if count:
        logger.info("Sent %d %s", count, name)
