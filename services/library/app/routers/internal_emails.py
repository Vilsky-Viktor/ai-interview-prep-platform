from fastapi import APIRouter

from app.schemas.emails import EmailPreferencesOut
from app.service_auth import ServiceCaller
from app.storage import emails

router = APIRouter(prefix="/internal/users", tags=["internal"])


@router.get("/{user_id}/email-preferences")
async def get_email_preferences(user_id: str, caller: ServiceCaller) -> EmailPreferencesOut:
    """For the services that send emails: what the user wants beyond service emails."""
    return EmailPreferencesOut(**await emails.preferences(user_id))
