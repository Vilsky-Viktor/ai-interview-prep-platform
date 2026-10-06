"""The admin zone's stats from rounds' records."""

from prepza_common.stats import counted
from sqlalchemy import func, select

from app.models.sessions import Session as RoundSession
from app.storage.db import Session


async def stats(month: str | None) -> dict[str, int]:
    """All time or in `month`: talents' free practice rounds, in the month each started. A round is
    one session per topic, all with the round's id in candidate_invite_id."""
    rounds = (
        select(func.min(RoundSession.started_at).label("started_at"))
        .where(RoundSession.practice)
        .group_by(RoundSession.candidate_invite_id)
        .subquery()
    )

    async with Session() as session:
        return {
            "practice": await counted(
                session, func.count(rounds.c.started_at), rounds.c.started_at, month
            ),
        }
