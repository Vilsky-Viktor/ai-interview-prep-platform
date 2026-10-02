from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def invite_undelivered(invite_id: str) -> None:
    response = await http.get_client().post(
        f"{settings.companies_url}/internal/invites/{invite_id}/undelivered",
        headers={"Authorization": f"Bearer {service_token('companies')}"},
    )

    response.raise_for_status()
