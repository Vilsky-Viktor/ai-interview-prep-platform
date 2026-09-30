from uuid import UUID

import httpx

from app.config.settings import settings
from app.service_auth import service_token


async def create_sessions(payload: dict) -> list[dict]:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=60) as client:
        response = await client.post(
            f"{settings.rounds_url}/internal/sessions",
            json=payload,
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    response.raise_for_status()

    return response.json()


async def invite_scores(invite_ids: list[UUID]) -> dict[str, dict]:
    if not invite_ids:
        return {}

    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.post(
            f"{settings.rounds_url}/internal/invite-scores",
            json={"invite_ids": [str(invite_id) for invite_id in invite_ids]},
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    response.raise_for_status()

    return response.json()


async def scorecard(invite_id: UUID) -> list[dict] | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.rounds_url}/internal/invites/{invite_id}/scorecard",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()
