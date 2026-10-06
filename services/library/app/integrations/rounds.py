from uuid import UUID

from prepza_common import http

from app.config.settings import settings
from app.service_auth import service_token


async def rescore_question(question_id: UUID, text: str, options: list[dict]) -> None:
    """Candidates who answered the question are marked again against its corrected key."""
    response = await http.get_client().post(
        f"{settings.rounds_url}/internal/questions/{question_id}/rescore",
        json={"text": text, "options": options},
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    response.raise_for_status()
