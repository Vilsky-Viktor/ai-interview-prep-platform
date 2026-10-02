from uuid import UUID

from fastapi import APIRouter
from prepza_common.auth import CurrentUser
from prepza_common.paging import PageParams

from app.helpers.rounds import round_out
from app.schemas.rounds import RoundOut
from app.storage import rounds

router = APIRouter(prefix="/topics", tags=["history"])


@router.get("/{topic_id}/rounds")
async def list_rounds(topic_id: UUID, user: CurrentUser, page: PageParams) -> list[RoundOut]:
    """The user's rounds on a topic, newest first, a page at a time."""
    rows = await rounds.list_for_topic(user.uid, topic_id, page.offset, page.limit)

    return [round_out(item) for item in rows]
