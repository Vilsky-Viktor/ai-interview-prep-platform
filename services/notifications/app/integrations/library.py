from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def share_undelivered(share_id: str) -> None:
    response = await http.get_client().post(
        f"{settings.library_url}/internal/shares/{share_id}/undelivered",
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    response.raise_for_status()
