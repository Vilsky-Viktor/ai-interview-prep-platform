import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.models.sharing import JoinedPreparation
from app.storage.db import Session


def join_statement(set_id: uuid.UUID, user_id: str):
    return (
        insert(JoinedPreparation)
        .values(set_id=set_id, user_id=user_id, joined_at=datetime.now(UTC))
        .on_conflict_do_nothing()
    )


async def is_joined(set_id: uuid.UUID, user_id: str) -> bool:
    query = select(JoinedPreparation.set_id).where(
        JoinedPreparation.set_id == set_id, JoinedPreparation.user_id == user_id
    )

    async with Session() as session:
        return await session.scalar(query) is not None


async def join(set_id: uuid.UUID, user_id: str) -> None:
    async with Session() as session:
        await session.execute(join_statement(set_id, user_id))
        await session.commit()


async def leave(set_id: uuid.UUID, user_id: str) -> None:
    async with Session() as session:
        await session.execute(
            delete(JoinedPreparation).where(
                JoinedPreparation.set_id == set_id, JoinedPreparation.user_id == user_id
            )
        )
        await session.commit()
