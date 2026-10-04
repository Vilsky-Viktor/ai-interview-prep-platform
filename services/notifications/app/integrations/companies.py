from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def invite_undelivered(invite_id: str) -> None:
    response = await http.get_client().post(
        f"{settings.companies_url}/internal/invites/{invite_id}/undelivered",
        headers={"Authorization": f"Bearer {service_token('companies')}"},
    )

    response.raise_for_status()


async def company_ids(user_id: str) -> list[str]:
    """Every company the user belongs to: they see its notifications too."""
    response = await http.get_client().get(
        f"{settings.companies_url}/internal/users/{user_id}/companies",
        headers={"Authorization": f"Bearer {service_token('companies')}"},
    )

    response.raise_for_status()

    return response.json()["company_ids"]
