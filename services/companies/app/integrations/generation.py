from uuid import UUID

import httpx
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def create(text: str, company_id: UUID, token: str) -> dict:
    response = await http.get_client().post(
        f"{settings.generation_url}/generations",
        json={"text": text, "kind": "interview", "company_id": str(company_id)},
        headers={"Authorization": f"Bearer {token}"},
    )

    response.raise_for_status()

    return response.json()


async def regenerate_question(question_id: UUID, set_id: UUID, user_id: str) -> httpx.Response:
    """The raw response, so the caller can pass rate limits and failures through."""
    return await http.get_client().post(
        f"{settings.generation_url}/internal/questions/{question_id}/regenerate",
        json={"user_id": user_id, "set_id": str(set_id)},
        headers={"Authorization": f"Bearer {service_token()}"},
        timeout=120,
    )


async def get(generation_id: UUID, company_id: UUID) -> dict | None:
    """Any member can see the company's generations, not only the admin who started one."""
    response = await http.get_client().get(
        f"{settings.generation_url}/internal/generations/{generation_id}",
        params={"company_id": str(company_id)},
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def review(generation_id: UUID, company_id: UUID, body: dict) -> httpx.Response:
    """The raw response, so the caller can pass a 409 (already reviewed) through."""
    return await http.get_client().post(
        f"{settings.generation_url}/internal/generations/{generation_id}/review",
        params={"company_id": str(company_id)},
        json=body,
        headers={"Authorization": f"Bearer {service_token()}"},
    )


async def cancel(generation_id: UUID, company_id: UUID) -> httpx.Response:
    """The raw response, so the caller can pass a 409 (already finished) through."""
    return await http.get_client().post(
        f"{settings.generation_url}/internal/generations/{generation_id}/cancel",
        params={"company_id": str(company_id)},
        headers={"Authorization": f"Bearer {service_token()}"},
    )


async def retry(generation_id: UUID, company_id: UUID) -> httpx.Response:
    """The raw response, so the caller can pass a 409 (not failed) through."""
    return await http.get_client().post(
        f"{settings.generation_url}/internal/generations/{generation_id}/retry",
        params={"company_id": str(company_id)},
        headers={"Authorization": f"Bearer {service_token()}"},
    )
