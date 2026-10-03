import uuid

from sqlalchemy import func, select

from app.models.certificates import Certificate
from app.storage.db import Session


async def get(certificate_id: uuid.UUID) -> Certificate | None:
    async with Session() as session:
        return await session.get(Certificate, certificate_id)


async def for_preparation(user_id: str, preparation_id: uuid.UUID) -> dict[uuid.UUID, uuid.UUID]:
    """Latest best-score certificate per topic on this preparation."""
    query = (
        select(Certificate.topic_id, Certificate.id)
        .where(Certificate.user_id == user_id, Certificate.preparation_id == preparation_id)
        .order_by(Certificate.score.desc(), Certificate.issued_at.desc())
    )
    certs: dict[uuid.UUID, uuid.UUID] = {}

    async with Session() as session:
        for topic_id, certificate_id in await session.execute(query):
            if topic_id not in certs:
                certs[topic_id] = certificate_id

        return certs


async def create(certificate: Certificate) -> Certificate:
    async with Session() as session:
        session.add(certificate)
        await session.commit()

        return certificate


async def has_for_topic(user_id: str, topic_id: uuid.UUID) -> bool:
    query = select(Certificate.id).where(
        Certificate.user_id == user_id, Certificate.topic_id == topic_id
    )

    async with Session() as session:
        return await session.scalar(query.limit(1)) is not None


async def mastered_counts(user_id: str, preparation_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    """Topics the user holds a certificate for, per preparation; preparations without any are
    missing."""
    query = (
        select(Certificate.preparation_id, func.count(Certificate.topic_id.distinct()))
        .where(Certificate.user_id == user_id, Certificate.preparation_id.in_(preparation_ids))
        .group_by(Certificate.preparation_id)
    )

    async with Session() as session:
        return dict((await session.execute(query)).all())
