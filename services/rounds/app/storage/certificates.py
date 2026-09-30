import uuid

from sqlalchemy import select

from app.models.certificates import Certificate
from app.models.rounds import Round
from app.storage.db import Session


async def get(certificate_id: uuid.UUID) -> tuple[Certificate, uuid.UUID] | None:
    query = (
        select(Certificate, Round.preparation_id)
        .join(Round, Round.id == Certificate.round_id)
        .where(Certificate.id == certificate_id)
    )

    async with Session() as session:
        return (await session.execute(query)).tuples().first()


async def for_preparation(
    user_id: str, preparation_id: uuid.UUID
) -> dict[uuid.UUID, uuid.UUID]:
    """Latest best-score certificate per topic on this preparation."""
    query = (
        select(Certificate.topic_id, Certificate.id)
        .join(Round, Round.id == Certificate.round_id)
        .where(Certificate.user_id == user_id, Round.preparation_id == preparation_id)
        .order_by(Certificate.score.desc(), Certificate.issued_at.desc())
    )
    certs: dict[uuid.UUID, uuid.UUID] = {}

    async with Session() as session:
        for topic_id, certificate_id in await session.execute(query):
            if topic_id not in certs:
                certs[topic_id] = certificate_id

        return certs


async def mastered_topics(user_id: str) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """Topics the user holds a certificate for, on any preparation."""
    query = (
        select(Round.preparation_id, Certificate.topic_id)
        .join(Round, Round.id == Certificate.round_id)
        .where(Certificate.user_id == user_id)
        .distinct()
    )

    async with Session() as session:
        rows = await session.execute(query)

        return [(preparation_id, topic_id) for preparation_id, topic_id in rows]
