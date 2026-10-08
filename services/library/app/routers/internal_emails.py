from fastapi import APIRouter

from app.constants.emails import ConsentSource
from app.schemas.emails import EmailPreferencesOut, RecipientsIn, RecipientsOut, UnsubscribeIn
from app.service_auth import ServiceCaller
from app.services.email_recipients import recipients
from app.storage import emails

router = APIRouter(prefix="/internal/users", tags=["internal"])


@router.get("/{user_id}/email-preferences")
async def get_email_preferences(user_id: str, caller: ServiceCaller) -> EmailPreferencesOut:
    """For the services that send emails: what the user wants beyond service emails."""
    return EmailPreferencesOut(**await emails.preferences(user_id))


@router.post("/{user_id}/unsubscribe")
async def unsubscribe(
    user_id: str, body: UnsubscribeIn, caller: ServiceCaller
) -> EmailPreferencesOut:
    """Notifications, for an email's unsubscribe link (checked there): turns the settings off,
    logged as an unsubscribe. Safe to repeat: a setting already off logs nothing."""
    changes = dict.fromkeys(body.settings, False)

    return EmailPreferencesOut(**await emails.change(user_id, changes, ConsentSource.UNSUBSCRIBE))


@router.post("/email-recipients")
async def email_recipients(body: RecipientsIn, caller: ServiceCaller) -> RecipientsOut:
    """Notifications, for its emails to many users at once (the activity digest, reminders): each
    user's address, interface language and preferences; users who are gone are left out."""
    return RecipientsOut(recipients=await recipients(body.user_ids))
