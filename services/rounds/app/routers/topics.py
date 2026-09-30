from uuid import UUID

from fastapi import APIRouter

from app.auth import CurrentUser
from app.helpers.rounds import round_out
from app.schemas.rounds import RoundOut
from app.storage import rounds

router = APIRouter(prefix="/topics", tags=["history"])


@router.get("/{topic_id}/rounds")
async def list_rounds(topic_id: UUID, user: CurrentUser) -> list[RoundOut]:
    """The user's rounds on a topic, newest first."""
    return [round_out(item) for item in await rounds.list_for_topic(user.uid, topic_id)]
