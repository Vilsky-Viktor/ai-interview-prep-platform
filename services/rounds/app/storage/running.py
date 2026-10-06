from datetime import UTC, datetime

from sqlalchemy import func, select

from app.constants.maintenance import RUNNING_WINDOW
from app.constants.rounds import RoundStatus
from app.models.sessions import Session
from app.storage.db import Session as Db


async def running_interviews() -> int:
    """Candidates' interviews with a question on screen now; previews and practice rounds stay
    out."""
    query = select(func.count(func.distinct(Session.candidate_invite_id))).where(
        Session.status == RoundStatus.IN_PROGRESS,
        ~Session.preview,
        ~Session.practice,
        Session.question_shown_at > datetime.now(UTC) - RUNNING_WINDOW,
    )

    async with Db() as db:
        return await db.scalar(query)
