import uuid

from app.constants.events import GENERATION_CANCELLED, GENERATION_COMPLETED
from app.helpers.notifications import interview_cancelled, interview_ready
from app.services import outbox as outbox_service
from app.storage import interviews


async def handle(event_type: str, data: dict) -> None:
    """Stores what an interview generation produced, or removes the interview of a cancelled
    one, and tells the company; other events aren't ours."""
    if event_type not in (GENERATION_COMPLETED, GENERATION_CANCELLED):
        return

    generation_id = uuid.UUID(data["generation_id"])
    interview = await interviews.get_for_generation(generation_id)

    # Already removed: nothing to store, nobody to tell.
    if interview is None:
        return

    if event_type == GENERATION_COMPLETED:
        await interviews.set_generated(
            generation_id,
            uuid.UUID(data["set_id"]),
            data["title"],
            interview_ready(interview, data["title"]),
        )
    else:
        await interviews.remove_for_generation(generation_id, interview_cancelled(interview))

    await outbox_service.flush_quietly()
