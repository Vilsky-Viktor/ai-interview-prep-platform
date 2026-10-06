from uuid import UUID

import httpx
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def create_sessions(payload: dict) -> list[dict]:
    response = await http.get_client().post(
        f"{settings.rounds_url}/internal/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


async def invite_scores(invite_ids: list[UUID]) -> dict[str, dict]:
    if not invite_ids:
        return {}

    response = await http.get_client().post(
        f"{settings.rounds_url}/internal/invite-scores",
        json={"invite_ids": [str(invite_id) for invite_id in invite_ids]},
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()

    return response.json()


async def delete_interview_data(set_id: UUID) -> None:
    response = await http.get_client().delete(
        f"{settings.rounds_url}/internal/interviews/{set_id}",
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()


async def scorecard(invite_id: UUID) -> list[dict] | None:
    response = await http.get_client().get(
        f"{settings.rounds_url}/internal/invites/{invite_id}/scorecard",
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def delete_invite_sessions(invite_ids: list[UUID]) -> None:
    """Deletes these candidates' sessions, answers and signals; raises if rounds can't."""
    response = await http.get_client().post(
        f"{settings.rounds_url}/internal/invites/delete",
        json={"invite_ids": [str(invite_id) for invite_id in invite_ids]},
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()


async def delete_user(user_id: str) -> None:
    response = await http.get_client().delete(
        f"{settings.rounds_url}/internal/users/{user_id}",
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()
