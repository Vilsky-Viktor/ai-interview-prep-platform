from datetime import datetime

from prepza_common.constants import DELETED_USER
from sqlalchemy import select, update

from app.constants.statuses import Status
from app.models.generation import Generation
from app.storage.checkpointer import delete_threads
from app.storage.db import Session

FINISHED = (Status.DONE, Status.FAILED, Status.CANCELLED)


async def delete_user(user_id: str) -> None:
    """Every generation belongs to a company, so it stays, without the user's id. Safe to
    repeat."""
    async with Session() as session:
        await session.execute(
            update(Generation).where(Generation.owner_uid == user_id).values(owner_uid=DELETED_USER)
        )
        await session.commit()


async def export(user_id: str) -> list[dict]:
    query = (
        select(Generation).where(Generation.owner_uid == user_id).order_by(Generation.created_at)
    )

    async with Session() as session:
        return [
            {
                "created_at": row.created_at,
                "status": row.status,
                "pasted_text": row.text,
                "topics": [topic.get("main_topic") for topic in row.topics or []],
            }
            for row in await session.scalars(query)
        ]


async def forget_texts(before: datetime, checkpointer) -> int:
    """Blanks the pasted texts of generations finished before `before`, and deletes the
    checkpoints still holding them; the saved tests stay. Returns how many."""
    async with Session() as session:
        ids = list(
            await session.scalars(
                update(Generation)
                .where(
                    Generation.status.in_(FINISHED),
                    Generation.updated_at < before,
                    Generation.text != "",
                )
                .values(text="")
                .returning(Generation.id)
            )
        )
        await session.commit()

    await delete_threads([str(item) for item in ids], checkpointer)

    return len(ids)
