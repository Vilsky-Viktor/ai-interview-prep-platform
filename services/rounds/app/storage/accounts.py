from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.helpers.export import answer_export
from app.models.sessions import Session
from app.models.talents import TalentLink
from app.storage.db import Session as Db


async def delete_user(user_id: str) -> None:
    """Everything rounds holds about a user: interview and practice sessions with their answers
    and signals, and their link to be suggested. Safe to repeat."""
    async with Db() as session:
        await session.execute(delete(Session).where(Session.user_id == user_id))
        await session.execute(delete(TalentLink).where(TalentLink.user_id == user_id))
        await session.commit()


async def export(user_id: str) -> dict:
    """The user's own data, in plain terms, for their data export."""
    async with Db() as session:
        sessions = await session.scalars(
            select(Session)
            .where(Session.user_id == user_id)
            .options(selectinload(Session.answers), selectinload(Session.signals))
        )

        link = await session.get(TalentLink, user_id)

        return {
            "suggested_to_companies": (
                {"url": link.url, "answered_at": link.decided_at} if link else None
            ),
            "interview_sections": [
                {
                    "topic": row.topic_title,
                    "status": row.status,
                    # A company's interview score isn't the candidate's to see; practice is.
                    "final_score": row.final_score if row.practice else None,
                    "started_at": row.started_at,
                    "answers": [
                        {**answer_export(row.questions, a, row.practice), "seconds": a.seconds}
                        for a in row.answers
                    ],
                    "page_leaves_and_copies": [
                        {"kind": s.kind, "question_id": s.question_id, "at": s.created_at}
                        for s in row.signals
                    ],
                }
                for row in sessions
            ],
        }
