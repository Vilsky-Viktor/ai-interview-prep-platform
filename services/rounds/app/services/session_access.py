from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.user import User

from app.constants.rounds import RoundStatus
from app.helpers.sessions import next_session_question, time_is_up
from app.models.rounds import Answer
from app.models.sessions import Session
from app.services.session_expiry import finish_if_expired
from app.storage import sessions


async def get_owned_session(session_id: UUID, user: User, grace_seconds: int = 0) -> Session:
    row = await sessions.get(session_id)

    if row is None or row.user_id != user.uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    # The question on screen ran out of time, even with the tab closed: it counts as wrong.
    if row.status == RoundStatus.IN_PROGRESS and time_is_up(row, datetime.now(UTC), grace_seconds):
        question = next_session_question(row)

        if question:
            await sessions.add_answer(
                Answer(
                    session_id=row.id,
                    question_id=question.question_id,
                    option_index=None,
                    correct=False,
                    score=0,
                    seconds=row.question_seconds,
                )
            )

        row = await sessions.get(session_id)

    # The whole interview ran out of time while the candidate was away: it's finished.
    if row.status == RoundStatus.IN_PROGRESS and await finish_if_expired(row.candidate_invite_id):
        row = await sessions.get(session_id)

    return row
