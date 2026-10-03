import uuid
from datetime import datetime

from sqlalchemy import text

from app.constants.rounds import INTERVIEW_TIME_MARGIN, RoundStatus
from app.storage.db import Session as Db

# Candidate interviews (all sessions of an invite) still in progress past their deadline: the
# start plus every question's seconds, plus the margin. Sessions from before every interview
# was timed have no seconds and never expire.
EXPIRED_SQL = text(
    """
    SELECT candidate_invite_id FROM sessions
    WHERE (CAST(:invite_id AS uuid) IS NULL OR candidate_invite_id = CAST(:invite_id AS uuid))
    GROUP BY candidate_invite_id
    HAVING bool_or(status = :in_progress)
        AND bool_and(question_seconds IS NOT NULL)
        AND min(started_at) + make_interval(
            secs => sum(jsonb_array_length(questions) * question_seconds) * (1 + :margin)
        ) < :now
    LIMIT :limit
    """
)


async def expired_invites(
    now: datetime, limit: int, invite_id: uuid.UUID | None = None
) -> list[uuid.UUID]:
    """Invites whose interview ran out of time; only `invite_id` when given."""
    params = {
        "invite_id": str(invite_id) if invite_id else None,
        "in_progress": RoundStatus.IN_PROGRESS,
        "margin": INTERVIEW_TIME_MARGIN,
        "now": now,
        "limit": limit,
    }

    async with Db() as session:
        return list(await session.scalars(EXPIRED_SQL, params))
