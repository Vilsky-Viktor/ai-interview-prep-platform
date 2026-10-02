import uuid

from app.constants.events import GENERATION_CANCELLED, GENERATION_COMPLETED
from app.storage import interviews


async def handle(event_type: str, data: dict) -> None:
    """Stores what an interview generation produced, or removes the interview of a cancelled
    one; other events aren't ours."""
    if event_type == GENERATION_COMPLETED:
        await interviews.set_generated(
            uuid.UUID(data["generation_id"]), uuid.UUID(data["set_id"]), data["title"]
        )
    elif event_type == GENERATION_CANCELLED:
        await interviews.remove_for_generation(uuid.UUID(data["generation_id"]))
