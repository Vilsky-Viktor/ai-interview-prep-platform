from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from prepza_common.auth import CurrentUser
from prepza_common.sse import event_stream

from app.schemas.notifications import FeedOut
from app.services.feed import feed, open_stream
from app.storage import notifications

router = APIRouter(prefix="/me", tags=["notifications"])


@router.get("")
async def get_feed(user: CurrentUser) -> FeedOut:
    """The bell: the latest notifications, the user's own and their companies', and how many
    came since they last opened it."""
    return await feed(user.uid)


@router.post("/seen", status_code=status.HTTP_204_NO_CONTENT)
async def mark_seen(user: CurrentUser) -> None:
    """Opening the bell: everything so far counts as read."""
    await notifications.mark_seen(user.uid)


@router.get("/stream")
async def stream(user: CurrentUser) -> StreamingResponse:
    """Server-sent events while a tab is open: {"new": true} as soon as a notification comes,
    so the bell reloads; heartbeat comments in between. At most MAX_STREAMS_PER_USER at once;
    the bell refreshes on its own without one."""
    return event_stream(await open_stream(user.uid))
