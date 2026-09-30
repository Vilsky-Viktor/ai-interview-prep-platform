import uuid

from app.models.rounds import Answer
from app.storage.db import Session


async def get(answer_id: uuid.UUID) -> Answer | None:
    async with Session() as session:
        return await session.get(Answer, answer_id)
