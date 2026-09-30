from uuid import UUID

import httpx

from app.config.settings import settings
from app.service_auth import service_token


async def get_set(set_id: UUID) -> dict | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.library_url}/internal/sets/{set_id}",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def rename_set(set_id: UUID, title: str) -> None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.patch(
            f"{settings.library_url}/internal/sets/{set_id}/title",
            json={"title": title},
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    response.raise_for_status()


async def get_topic_questions(set_id: UUID, topic_id: UUID) -> list[dict] | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.library_url}/internal/sets/{set_id}/topics/{topic_id}/questions",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_question_reports(set_id: UUID, question_id: UUID) -> list[dict] | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.library_url}/internal/sets/{set_id}/questions/{question_id}/reports",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_content(set_id: UUID) -> dict | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.library_url}/internal/sets/{set_id}/content",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()
