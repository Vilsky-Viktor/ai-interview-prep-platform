from uuid import UUID

import httpx
from prepza_common import http
from prepza_common.paging import Page

from app.config.settings import settings
from app.service_auth import service_token


async def get_set(set_id: UUID) -> dict | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}",
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def rename_set(set_id: UUID, title: str) -> None:
    response = await http.get_client().patch(
        f"{settings.library_url}/internal/sets/{set_id}/title",
        json={"title": title},
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    response.raise_for_status()


async def delete_interview(set_id: UUID) -> None:
    response = await http.get_client().delete(
        f"{settings.library_url}/internal/interviews/{set_id}",
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    response.raise_for_status()


async def get_topic_questions(set_id: UUID, topic_id: UUID) -> list[dict] | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}/topics/{topic_id}/questions",
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_question_reports(set_id: UUID, question_id: UUID, page: Page) -> list[dict] | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}/questions/{question_id}/reports",
        params={"offset": page.offset, "limit": page.limit},
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_content(set_id: UUID) -> dict | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}/content",
        headers={"Authorization": f"Bearer {service_token('library')}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()
