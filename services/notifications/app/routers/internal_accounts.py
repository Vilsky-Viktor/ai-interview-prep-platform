from fastapi import APIRouter, status
from prepza_common.notifications import Recipient

from app.schemas.notifications import NotificationOut
from app.service_auth import ServiceCaller
from app.storage import notifications

router = APIRouter(prefix="/internal", tags=["internal"])


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, email: str, caller: ServiceCaller) -> None:
    """Library, deleting an account: the user's own notifications go, and companies'
    notifications about them as a candidate (their email and grade)."""
    await notifications.remove_user(user_id)
    await notifications.remove_candidate(email)


@router.get("/users/{user_id}/export")
async def export_user(user_id: str, caller: ServiceCaller) -> dict:
    """Library, for "Download my data": the user's own notifications."""
    items = await notifications.latest([(Recipient.USER, user_id)], limit=None)

    return {"notifications": [NotificationOut.model_validate(item) for item in items]}
