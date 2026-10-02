from uuid import UUID

from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def delete_preparation_data(preparation_id: UUID) -> None:
    """Deletes rounds, answers and progress on the preparation; raises if rounds can't."""
    response = await http.get_client().delete(
        f"{settings.rounds_url}/internal/preparations/{preparation_id}",
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()


async def mastered_counts(user_id: str, preparation_ids: list[UUID]) -> dict[str, int]:
    """Topics the user holds a certificate for, per preparation id."""
    response = await http.get_client().post(
        f"{settings.rounds_url}/internal/mastered-counts",
        json={"user_id": user_id, "preparation_ids": [str(item) for item in preparation_ids]},
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()

    return response.json()
