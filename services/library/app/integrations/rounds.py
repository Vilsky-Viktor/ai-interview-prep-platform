from uuid import UUID

from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def delete_preparation_data(preparation_id: UUID) -> None:
    """Deletes rounds, answers and progress on the preparation; raises if rounds can't."""
    response = await http.get_client().delete(
        f"{settings.rounds_url}/internal/preparations/{preparation_id}",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()
