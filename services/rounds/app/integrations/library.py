from uuid import UUID

import httpx
from prepza_common import http

from app.config.settings import settings
from app.schemas.library import TopicQuestions
from app.service_auth import service_token


async def get_set(set_id: UUID) -> dict | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_question_texts(set_id: UUID) -> dict[str, str] | None:
    """Current text per question id of a set, without answers."""
    response = await http.get_client().get(
        f"{settings.library_url}/internal/sets/{set_id}/question-texts",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return response.json()


async def get_topic_questions(topic_id: UUID, user_id: str) -> TopicQuestions | None:
    """The topic's questions with answers, or None if it doesn't exist or the user has no access."""
    response = await http.get_client().get(
        f"{settings.library_url}/internal/topics/{topic_id}",
        params={"user_id": user_id},
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return TopicQuestions.model_validate(response.json())
