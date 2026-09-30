import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.constants.rounds import RoundStatus
from app.helpers.rounds import round_questions
from app.models.certificates import Certificate
from app.models.rounds import Answer, Round
from app.schemas.library import TopicQuestions
from app.storage.db import Session

LOAD_ROUND = [selectinload(Round.answers), selectinload(Round.certificate)]


async def get_in_progress(user_id: str, topic_id: uuid.UUID, mode: str) -> Round | None:
    query = (
        select(Round)
        .where(
            Round.user_id == user_id,
            Round.topic_id == topic_id,
            Round.mode == mode,
            Round.status == RoundStatus.IN_PROGRESS,
        )
        .options(*LOAD_ROUND)
        .order_by(Round.started_at.desc())
        .limit(1)
    )

    async with Session() as session:
        return await session.scalar(query)


async def create(
    user_id: str, topic: TopicQuestions, mode: str, latest: dict[str, int]
) -> Round:
    new_round = Round(
        user_id=user_id,
        topic_id=topic.id,
        preparation_id=topic.preparation_id,
        topic_title=topic.title,
        mode=mode,
        status=RoundStatus.IN_PROGRESS,
        questions=round_questions(topic, latest),
        final_score=None,
        finished_at=None,
        answers=[],
        certificate=None,
    )

    async with Session() as session:
        session.add(new_round)
        await session.commit()

    return new_round


async def get(round_id: uuid.UUID) -> Round | None:
    async with Session() as session:
        return await session.get(Round, round_id, options=LOAD_ROUND)


async def list_for_topic(user_id: str, topic_id: uuid.UUID) -> list[Round]:
    query = (
        select(Round)
        .where(Round.user_id == user_id, Round.topic_id == topic_id)
        .options(*LOAD_ROUND)
        .order_by(Round.started_at.desc())
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def best_for_preparation(
    user_id: str, preparation_id: uuid.UUID
) -> list[tuple[uuid.UUID, str, int]]:
    """Best finished score per topic and mode."""
    query = (
        select(Round.topic_id, Round.mode, func.max(Round.final_score))
        .where(
            Round.user_id == user_id,
            Round.preparation_id == preparation_id,
            Round.status == RoundStatus.FINISHED,
        )
        .group_by(Round.topic_id, Round.mode)
    )

    async with Session() as session:
        rows = await session.execute(query)

        return [(topic_id, mode, score) for topic_id, mode, score in rows]


async def add_answer(answer: Answer) -> bool:
    """Stores the answer; False if this question was already answered in the round."""
    async with Session() as session:
        session.add(answer)

        try:
            await session.commit()
        except IntegrityError:
            return False

    return True


async def finish(round_id: uuid.UUID, final_score: int, certificate: Certificate | None) -> None:
    """Marks the round finished and issues the certificate, once, in one transaction."""
    async with Session() as session:
        result = await session.execute(
            update(Round)
            .where(Round.id == round_id, Round.status == RoundStatus.IN_PROGRESS)
            .values(
                status=RoundStatus.FINISHED,
                final_score=final_score,
                finished_at=datetime.now(UTC),
            )
        )

        if result.rowcount == 1 and certificate is not None:
            session.add(certificate)

        await session.commit()


async def remove(round_id: uuid.UUID, user_id: str) -> list[uuid.UUID] | None:
    """Deletes the round; returns the questions it answered, or None if it isn't the user's."""
    async with Session() as session:
        question_ids = list(
            await session.scalars(select(Answer.question_id).where(Answer.round_id == round_id))
        )
        result = await session.execute(
            delete(Round).where(Round.id == round_id, Round.user_id == user_id)
        )
        await session.commit()

        return question_ids if result.rowcount == 1 else None
