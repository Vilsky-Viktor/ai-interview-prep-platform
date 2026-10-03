from fastapi import APIRouter, status
from prepza_common.google import Invoker

from app.services import outbox as outbox_service
from app.services.session_expiry import finish_expired

router = APIRouter(prefix="/internal/schedules", tags=["schedules"], dependencies=[Invoker])


@router.post("/outbox", status_code=status.HTTP_204_NO_CONTENT)
async def flush_outbox() -> None:
    """Every minute, from Cloud Scheduler: publishes events that weren't published right after
    their change."""
    await outbox_service.flush()


@router.post("/expire-interviews", status_code=status.HTTP_204_NO_CONTENT)
async def expire_interviews() -> None:
    """Every minute, from Cloud Scheduler: finishes interviews whose time ran out after the
    candidate left, so companies see them as finished."""
    await finish_expired()
