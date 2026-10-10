from uuid import UUID

import httpx
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def company_paid(company_id: UUID) -> bool:
    """Whether the company ever topped up. When billing can't say, it counts as not: the turn
    is then held to the limits for everyone, rather than refused."""
    try:
        response = await http.get_client().get(
            f"{settings.billing_url}/internal/companies/{company_id}/paid",
            headers={"Authorization": f"Bearer {service_token('billing')}"},
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return False

    return response.json()["paid"]
