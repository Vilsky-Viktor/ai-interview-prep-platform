import httpx
from prepza_common import http

from app.config.settings import settings


async def catalog() -> dict | None:
    """Billing's public prices; None when billing can't be reached, so help still answers."""
    try:
        response = await http.get_client().get(f"{settings.billing_url}/catalog")
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    return response.json()
