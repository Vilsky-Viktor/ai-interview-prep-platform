from uuid import UUID

import httpx

from app.config.settings import settings
from app.schemas.library import PreparationIn
from app.schemas.regenerate import QuestionContext, RegeneratedQuestion
from app.service_auth import service_token


async def _post(path: str, preparation: PreparationIn) -> UUID:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.post(
            f"{settings.library_url}{path}",
            json=preparation.model_dump(),
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    response.raise_for_status()

    return UUID(response.json()["id"])


async def create_preparation(preparation: PreparationIn) -> UUID:
    return await _post("/internal/preparations", preparation)


async def create_interview(preparation: PreparationIn) -> UUID:
    return await _post("/internal/interviews", preparation)


async def get_question_context(question_id: UUID) -> QuestionContext | None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.get(
            f"{settings.library_url}/internal/questions/{question_id}/context",
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    if response.status_code == httpx.codes.NOT_FOUND:
        return None

    response.raise_for_status()

    return QuestionContext.model_validate(response.json())


async def replace_question(question_id: UUID, question: RegeneratedQuestion) -> None:
    transport = httpx.AsyncHTTPTransport(retries=3)

    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        response = await client.put(
            f"{settings.library_url}/internal/questions/{question_id}",
            json=question.model_dump(),
            headers={"Authorization": f"Bearer {service_token()}"},
        )

    response.raise_for_status()
