from prepza_common.notifications import NotificationKind, Recipient

from app.config.settings import settings
from app.helpers.member_emails import top_up_failed_email
from app.integrations import companies, library
from app.services import delivery


async def top_up_failed(data: dict, key: str) -> None:
    """A failed automatic top-up, emailed at once to the company's owners and admins, whatever
    their email settings: it's about the company's billing. Keyed by the notification and the
    user, so a retried event sends nobody a second email."""
    if (
        data["kind"] != NotificationKind.AUTO_TOP_UP_FAILED
        or data["recipient"] != Recipient.COMPANY
    ):
        return

    found = await companies.members([data["recipient_id"]])

    if not found:
        return

    [company] = found
    editors = [member["user_id"] for member in company["members"] if member["editor"]]

    for recipient in await library.recipients(editors):
        email = top_up_failed_email(recipient, company["name"], settings.site_url)
        await delivery.send(email, f"events/{key}/{recipient['user_id']}")
