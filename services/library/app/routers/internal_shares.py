from uuid import UUID

from fastapi import APIRouter, status

from app.service_auth import ServiceCaller
from app.storage import shares

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/shares/{share_id}/undelivered", status_code=status.HTTP_204_NO_CONTENT)
async def share_undelivered(share_id: UUID, caller: ServiceCaller) -> None:
    """Notifications reports a bounced or spam-flagged share email; safe to repeat."""
    await shares.mark_undelivered(share_id)
