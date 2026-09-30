import uuid

from sqlalchemy import select

from app.constants.rounds import ChatRole
from app.models.chat import ChatMessage
from app.storage.db import Session


async def list_messages(answer_id: uuid.UUID) -> list[ChatMessage]:
    query = (
        select(ChatMessage)
        .where(ChatMessage.answer_id == answer_id)
        .order_by(ChatMessage.created_at)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def add_exchange(answer_id: uuid.UUID, message: str, reply: str) -> None:
    async with Session() as session:
        session.add(ChatMessage(answer_id=answer_id, role=ChatRole.USER, content=message))
        # Separate flushes give the reply a later created_at, so it always sorts after the question.
        await session.flush()
        session.add(ChatMessage(answer_id=answer_id, role=ChatRole.ASSISTANT, content=reply))
        await session.commit()
