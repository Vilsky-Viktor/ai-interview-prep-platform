from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select

from app.models.conversations import Conversation
from app.storage.db import Session


async def create(user_id: str, company_id: UUID | None, title: str) -> Conversation:
    async with Session() as session:
        conversation = Conversation(user_id=user_id, company_id=company_id, title=title)
        session.add(conversation)
        await session.commit()

        return conversation


async def owned(conversation_id: UUID, user_id: str) -> Conversation | None:
    """The user's own conversation; None when it's gone or someone else's."""
    async with Session() as session:
        return await session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )


async def of_user(
    user_id: str, company_id: UUID | None, offset: int, limit: int
) -> list[Conversation]:
    """The user's conversations, the latest first; about one company when it's given."""
    query = select(Conversation).where(Conversation.user_id == user_id)

    if company_id is not None:
        query = query.where(Conversation.company_id == company_id)

    query = query.order_by(Conversation.updated_at.desc(), Conversation.id)

    async with Session() as session:
        return list(await session.scalars(query.offset(offset).limit(limit)))


async def delete_one(conversation_id: UUID) -> None:
    """With its messages and their tool calls (the foreign keys cascade)."""
    async with Session() as session:
        await session.execute(delete(Conversation).where(Conversation.id == conversation_id))
        await session.commit()


async def delete_idle(before: datetime, limit: int) -> int:
    """Up to `limit` conversations nobody added to since `before`; how many went."""
    idle = (
        select(Conversation.id).where(Conversation.updated_at < before).limit(limit)
    ).scalar_subquery()

    async with Session() as session:
        result = await session.execute(delete(Conversation).where(Conversation.id.in_(idle)))
        await session.commit()

        return result.rowcount


async def delete_company(company_id: UUID) -> int:
    """Every conversation about the company; how many went (none when run again)."""
    async with Session() as session:
        result = await session.execute(
            delete(Conversation).where(Conversation.company_id == company_id)
        )
        await session.commit()

        return result.rowcount


async def delete_user(user_id: str) -> None:
    async with Session() as session:
        await session.execute(delete(Conversation).where(Conversation.user_id == user_id))
        await session.commit()
