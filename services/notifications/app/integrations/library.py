from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def unsubscribe(user_id: str, email_settings: list[str]) -> None:
    """Turns the user's email settings off, logged as an unsubscribe; safe to repeat."""
    response = await http.get_client().post(
        f"{settings.library_url}/internal/users/{user_id}/unsubscribe",
        json={"settings": email_settings},
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    response.raise_for_status()
