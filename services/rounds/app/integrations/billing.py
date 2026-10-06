import httpx
from prepza_common import http, memory_cache

from app.config.settings import settings
from app.constants.help import CATALOG_CACHE_SECONDS, CATALOG_KEY


async def catalog() -> dict | None:
    """Billing's public prices, kept for a few minutes; None when billing can't be reached, so
    help still answers."""
    cached = memory_cache.get(CATALOG_KEY)

    if cached is not None:
        return cached

    try:
        response = await http.get_client().get(f"{settings.billing_url}/catalog")
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    prices = response.json()
    memory_cache.put(CATALOG_KEY, prices, CATALOG_CACHE_SECONDS)

    return prices
