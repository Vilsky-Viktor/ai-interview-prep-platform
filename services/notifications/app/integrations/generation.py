from app.config.settings import settings
from app.integrations.batches import post_ids
from app.service_auth import service_token


async def statuses(generation_ids: list[str]) -> list[dict]:
    """Each of those generations that still exists: {"id", "status", "owner_uid",
    "updated_at"}."""
    url = f"{settings.generation_url}/internal/generations/statuses"

    return await post_ids(url, service_token("generation"), "ids", generation_ids, "generations")
