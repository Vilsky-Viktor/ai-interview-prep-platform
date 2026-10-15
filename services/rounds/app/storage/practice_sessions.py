import uuid

from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.models.sessions import Session
from app.storage.db import Session as Db


def _practice(user_id: str, template_id: uuid.UUID):
    return (
        Session.user_id == user_id,
        Session.interview_set_id == template_id,
        Session.practice.is_(True),
    )


async def practiced(user_id: str, template_id: uuid.UUID) -> bool:
    """Whether the talent took a practice round on the template before."""
    async with Db() as session:
        return bool(await session.scalar(select(exists().where(*_practice(user_id, template_id)))))


async def practice_for_user(user_id: str, template_id: uuid.UUID) -> list[Session]:
    """Every practice section the talent took on the template, with answers."""
    query = (
        select(Session)
        .where(*_practice(user_id, template_id))
        .options(selectinload(Session.answers))
    )

    async with Db() as session:
        return list(await session.scalars(query))
