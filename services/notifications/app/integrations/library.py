from prepza_common import http

from app.config.settings import settings
from app.integrations.batches import post_ids
from app.service_auth import service_token


async def unsubscribe(user_id: str, email_settings: list[str]) -> None:
    """Turns the user's email settings off, logged as an unsubscribe; safe to repeat."""
    response = await http.get_client().post(
        f"{settings.library_url}/internal/users/{user_id}/unsubscribe",
        json={"settings": email_settings},
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    response.raise_for_status()


async def recipients(user_ids: list[str]) -> list[dict]:
    """Each user's address, interface language and email preferences: {"user_id", "email",
    "language", "preferences"}; users who are gone are left out."""
    url = f"{settings.library_url}/internal/users/email-recipients"

    return await post_ids(url, service_token("library"), "user_ids", user_ids, "recipients")
