from uuid import UUID

from fastapi import APIRouter, status

from app.service_auth import ServiceCaller
from app.storage import invites

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/invites/{invite_id}/undelivered", status_code=status.HTTP_204_NO_CONTENT)
async def invite_undelivered(invite_id: UUID, caller: ServiceCaller) -> None:
    """Notifications reports a bounced or spam-flagged invite email; safe to repeat."""
    await invites.mark_undelivered(invite_id)
