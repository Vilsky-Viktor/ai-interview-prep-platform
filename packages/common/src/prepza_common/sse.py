"""Server-sent events: the help chat's and the assistant's streamed answers, the bell's stream."""

import json
from collections.abc import AsyncIterator

from fastapi.responses import StreamingResponse

# A comment line: it keeps the connection open through proxies, and clients skip it.
KEEP_ALIVE = ": keep-alive\n\n"


def sse_event(data: dict) -> str:
    """One event carrying `data` as JSON."""
    return f"data: {json.dumps(data)}\n\n"


def event_stream(events: AsyncIterator[str]) -> StreamingResponse:
    """A response streaming `events` as they come."""
    return StreamingResponse(
        events,
        media_type="text/event-stream",
        # Tells nginx not to buffer the stream.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
