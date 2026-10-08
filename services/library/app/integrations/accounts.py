from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


def services() -> dict[str, str]:
    """The services that hold their own part of a user's data, by name."""
    return {
        "companies": settings.companies_url,
        "rounds": settings.rounds_url,
        "generation": settings.generation_url,
        "billing": settings.billing_url,
        "notifications": settings.notifications_url,
        "ats": settings.ats_url,
        "api": settings.api_url,
    }


async def delete_user(service: str, user_id: str, email: str) -> None:
    """Deletes the user's data in one service; raises if it can't, so deletion can be retried."""
    # The email goes in the body, never the query string, which request logs record.
    response = await http.get_client().request(
        "DELETE",
        f"{services()[service]}/internal/users/{user_id}",
        json={"email": email},
        headers={"Authorization": f"Bearer {service_token(service)}"},
    )

    response.raise_for_status()


async def export_user(service: str, user_id: str, email: str) -> dict:
    response = await http.get_client().post(
        f"{services()[service]}/internal/users/{user_id}/export",
        json={"email": email},
        headers={"Authorization": f"Bearer {service_token(service)}"},
    )

    response.raise_for_status()

    return response.json()
