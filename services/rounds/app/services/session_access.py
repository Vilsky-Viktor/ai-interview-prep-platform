from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.user import User

from app.models.sessions import Session
from app.storage import sessions


async def get_owned_session(session_id: UUID, user: User) -> Session:
    row = await sessions.get(session_id)

    if row is None or row.user_id != user.uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    return row
