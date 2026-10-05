from uuid import UUID

from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def verify_question(question_id: UUID, flag: str, now: bool = False) -> None:
    """Queues the verifier for a newly flagged question; raises if generation can't."""
    response = await http.get_client().post(
        f"{settings.generation_url}/internal/questions/{question_id}/verify",
        json={"flag": flag, "now": now},
        headers={"Authorization": f"Bearer {service_token('generation')}"},
    )

    response.raise_for_status()
