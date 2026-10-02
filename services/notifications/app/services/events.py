from app.config.settings import settings
from app.constants.events import CANDIDATE_INVITED, PREPARATION_SHARED
from app.helpers.emails import candidate_invite_email, share_invite_email
from app.integrations import resend, smtp
from app.models.email import Email


async def deliver(email: Email, message_id: str) -> None:
    if settings.resend_api_key:
        # Pub/Sub's message id as the key, so a retried event never sends the email twice.
        await resend.send(email, f"events/{message_id}")

        return

    await smtp.send(email)


async def handle(event_type: str, data: dict, message_id: str) -> None:
    """Sends the email an event asks for; other events aren't ours."""
    if event_type == PREPARATION_SHARED:
        await deliver(share_invite_email(data, settings.site_url), message_id)

    if event_type == CANDIDATE_INVITED:
        await deliver(candidate_invite_email(data, settings.site_url), message_id)
