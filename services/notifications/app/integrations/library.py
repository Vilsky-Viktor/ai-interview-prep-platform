from prepza_common import http
from prepza_common.http import bearer

from app.config.settings import settings
from app.integrations.batches import post_ids
from app.service_auth import service_token


async def unsubscribe(user_id: str, email_settings: list[str]) -> None:
    """Turns the user's email settings off, logged as an unsubscribe; safe to repeat."""
    response = await http.get_client().post(
        f"{settings.library_url}/internal/users/{user_id}/unsubscribe",
        json={"settings": email_settings},
        headers=bearer(service_token("library")),
    )

    response.raise_for_status()


async def recipients(user_ids: list[str]) -> list[dict]:
    """Each user's address, interface language and email preferences: {"user_id", "email",
    "language", "preferences"}; users who are gone are left out."""
    url = f"{settings.library_url}/internal/users/email-recipients"

    return await post_ids(url, service_token("library"), "user_ids", user_ids, "recipients")


async def user_ids() -> list[str]:
    """Every account, for a notice about the terms or the privacy policy."""
    response = await http.get_client().get(
        f"{settings.library_url}/internal/users/ids",
        headers=bearer(service_token("library")),
    )

    response.raise_for_status()

    return response.json()["user_ids"]
