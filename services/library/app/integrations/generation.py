from uuid import UUID

import httpx
from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def verify_question(question_id: UUID, flag: str) -> None:
    """Queues the verifier for a newly flagged question; raises if generation can't."""
    response = await http.get_client().post(
        f"{settings.generation_url}/internal/questions/{question_id}/verify",
        json={"flag": flag},
        headers={"Authorization": f"Bearer {service_token('generation')}"},
    )

    response.raise_for_status()


async def regenerate_question(question_id: UUID, set_id: UUID, user_id: str) -> httpx.Response:
    """The raw response, so the caller can pass rate limits and failures through."""
    return await http.get_client().post(
        f"{settings.generation_url}/internal/questions/{question_id}/regenerate",
        json={"user_id": user_id, "set_id": str(set_id)},
        headers={"Authorization": f"Bearer {service_token('generation')}"},
        # Writing a question and its options waits on the LLM.
        timeout=120,
    )


async def title_has_company(title: str) -> bool:
    """Whether the title names a company; raises if generation can't tell."""
    response = await http.get_client().post(
        f"{settings.generation_url}/internal/titles/check",
        json={"title": title},
        headers={"Authorization": f"Bearer {service_token('generation')}"},
        # One short LLM call.
        timeout=30,
    )
    response.raise_for_status()

    return response.json()["has_company"]
