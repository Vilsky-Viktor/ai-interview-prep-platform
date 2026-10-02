from uuid import UUID

import httpx
from prepza_common import http
from prepza_common.sets import PreparationIn, QuestionIn

from app.config.settings import settings
from app.schemas.library import ReuseIn
from app.schemas.regenerate import QuestionContext, RegeneratedQuestion
from app.schemas.verify import QuestionQuality
from app.service_auth import service_token


async def _post(path: str, preparation: PreparationIn) -> UUID:
    response = await http.get_client().post(
        f"{settings.library_url}{path}",
        json=preparation.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()

    return UUID(response.json()["id"])


async def create_preparation(preparation: PreparationIn) -> UUID:
    return await _post("/internal/preparations", preparation)


async def create_interview(preparation: PreparationIn) -> UUID:
    return await _post("/internal/interviews", preparation)


async def get_question_context(question_id: UUID) -> QuestionContext | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/questions/{question_id}/context",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return QuestionContext.model_validate(response.json())


async def replace_question(question_id: UUID, question: RegeneratedQuestion) -> None:
    response = await http.get_client().put(
        f"{settings.library_url}/internal/questions/{question_id}",
        json=question.model_dump(),
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()


async def get_question_quality(question_id: UUID) -> QuestionQuality | None:
    response = await http.get_client().get(
        f"{settings.library_url}/internal/questions/{question_id}/quality",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return QuestionQuality.model_validate(response.json())


async def keep_question(question_id: UUID) -> None:
    response = await http.get_client().post(
        f"{settings.library_url}/internal/questions/{question_id}/keep",
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()


async def find_reusable(request: ReuseIn) -> list[QuestionIn]:
    """Proven questions from public preparations on a similar topic."""
    response = await http.get_client().post(
        f"{settings.library_url}/internal/reuse",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()

    return [QuestionIn.model_validate(item) for item in response.json()]


async def missing_embeddings(limit: int) -> list[dict]:
    """Preparation topics saved before embeddings existed: [{"id", "title", "subtopics"}]."""
    response = await http.get_client().get(
        f"{settings.library_url}/internal/embeddings/missing",
        params={"limit": limit},
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()

    return response.json()


async def save_embeddings(embeddings: dict[str, list[float]]) -> None:
    response = await http.get_client().put(
        f"{settings.library_url}/internal/embeddings",
        json=[{"id": topic_id, "embedding": value} for topic_id, value in embeddings.items()],
        headers={"Authorization": f"Bearer {service_token()}"},
    )

    response.raise_for_status()
