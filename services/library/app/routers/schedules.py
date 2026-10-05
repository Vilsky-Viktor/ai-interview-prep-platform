import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.constants.reuse import REVEAL_AFTER_IDLE_DAYS
from app.services import outbox as outbox_service
from app.storage import bank

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
    revealed (constants/sets.py Stage)."""
    idle_since = datetime.now(UTC) - timedelta(days=REVEAL_AFTER_IDLE_DAYS)
    retired, revealed = await bank.move_stages(idle_since)
    logger.info("Bank: %d questions retired, %d revealed", retired, revealed)
