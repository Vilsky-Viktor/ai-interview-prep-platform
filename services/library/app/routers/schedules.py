import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.constants.events import PROCESSED_EVENT_DAYS
from app.constants.reuse import REVEAL_AFTER_IDLE_DAYS
from app.services import news as news_service
from app.services import outbox as outbox_service
from app.services import quality as quality_service
from app.storage import bank, processed_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/outbox", status_code=status.HTTP_204_NO_CONTENT)
async def flush_outbox() -> None:
    """Every minute, from Cloud Scheduler: publishes events that weren't published right after
    their change."""
    await outbox_service.flush()


@router.post("/bank", status_code=status.HTTP_204_NO_CONTENT)
async def move_bank_stages() -> None:
    """Daily, from Cloud Scheduler: bank questions move one way, private to retiring to
    revealed (constants/sets.py Stage). The same daily run sends flags the verifier hasn't acted
    on to it again, and forgets old notes of processed events."""
    now = datetime.now(UTC)
    retired, revealed = await bank.move_stages(now - timedelta(days=REVEAL_AFTER_IDLE_DAYS))
    logger.info("Bank: %d questions retired, %d revealed", retired, revealed)
    resent = await quality_service.resend_stale_flags()
    logger.info("Sent %d flagged questions to the verifier again", resent)
    untranslated = await news_service.resend_untranslated()
    logger.info("Sent %d news posts to be translated again", untranslated)
    await processed_events.forget(now - timedelta(days=PROCESSED_EVENT_DAYS))
