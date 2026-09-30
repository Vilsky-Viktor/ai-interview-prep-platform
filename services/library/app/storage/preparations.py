import uuid

from sqlalchemy import Row, delete, func, select, update
from sqlalchemy.orm import selectinload

from app.constants.sets import OwnerType, SetKind, Visibility
from app.models.feedback import QuestionRating, QuestionReport
from app.models.sets import Question, QuestionSet, Topic
from app.models.sharing import JoinedPreparation
from app.schemas.preparations import PreparationIn
from app.storage.db import Session
from app.storage.stats import summary_columns


def _topics(preparation: PreparationIn) -> list[Topic]:
    return [
        Topic(
            position=ti,
            title=topic.title,
            subtopics=topic.subtopics,
            questions=[
                Question(
                    position=qi,
                    text=question.text,
                    reference_answer=question.reference_answer,
                    options=[option.model_dump() for option in question.options],
                )
                for qi, question in enumerate(topic.questions)
            ],
        )
        for ti, topic in enumerate(preparation.topics)
    ]


async def create(preparation: PreparationIn) -> uuid.UUID:
    question_set = QuestionSet(
        kind=SetKind.PREPARATION,
        owner_type=OwnerType.USER,
        owner_id=preparation.owner_uid,
        title=preparation.title,
        source_text=preparation.source_text,
        level=preparation.level,
        requirements=preparation.requirements,
        topics=_topics(preparation),
    )

    async with Session() as session:
        session.add(question_set)
        await session.flush()
        session.add(
            JoinedPreparation(set_id=question_set.id, user_id=preparation.owner_uid)
        )
        await session.commit()

    return question_set.id


async def create_interview(payload: PreparationIn) -> uuid.UUID:
    """Company interviews are always private."""
    question_set = QuestionSet(
        kind=SetKind.INTERVIEW,
        owner_type=OwnerType.COMPANY,
        owner_id=payload.owner_uid,
        title=payload.title,
        source_text=payload.source_text,
        level=payload.level,
        requirements=payload.requirements,
        visibility=Visibility.PRIVATE,
        topics=_topics(payload),
    )

    async with Session() as session:
        session.add(question_set)
        await session.commit()

    return question_set.id


async def get_content(set_id: uuid.UUID) -> QuestionSet | None:
    """A set with every topic and question, for starting candidate sessions."""
    query = (
        select(QuestionSet)
        .where(QuestionSet.id == set_id)
        .options(selectinload(QuestionSet.topics).selectinload(Topic.questions))
    )

    async with Session() as session:
        return await session.scalar(query)


async def question_texts(set_id: uuid.UUID) -> list[tuple[uuid.UUID, str]]:
    """Id and text of every question in a set, without answers or options."""
    query = (
        select(Question.id, Question.text)
        .join(Topic, Topic.id == Question.topic_id)
        .where(Topic.set_id == set_id)
    )

    async with Session() as session:
        return [(question_id, text) for question_id, text in await session.execute(query)]


async def list_for_owner(owner_uid: str) -> list[Row]:
    query = (
        select(QuestionSet, *summary_columns())
        .where(
            QuestionSet.kind == SetKind.PREPARATION,
            QuestionSet.owner_type == OwnerType.USER,
            QuestionSet.owner_id == owner_uid,
        )
        .order_by(QuestionSet.created_at.desc())
    )

    async with Session() as session:
        return list(await session.execute(query))


async def list_joined(user_id: str) -> list[Row]:
    query = (
        select(QuestionSet, *summary_columns())
        .join(JoinedPreparation, JoinedPreparation.set_id == QuestionSet.id)
        .where(
            JoinedPreparation.user_id == user_id,
            QuestionSet.owner_id != user_id,
        )
        .order_by(JoinedPreparation.joined_at.desc())
    )

    async with Session() as session:
        return list(await session.execute(query))


async def get(set_id: uuid.UUID) -> QuestionSet | None:
    async with Session() as session:
        return await session.get(QuestionSet, set_id)


async def get_summary(set_id: uuid.UUID) -> Row | None:
    query = select(QuestionSet, *summary_columns()).where(
        QuestionSet.id == set_id, QuestionSet.kind == SetKind.PREPARATION
    )

    async with Session() as session:
        return (await session.execute(query)).first()


async def get_topics(set_id: uuid.UUID) -> list[tuple[Topic, int]]:
    """Topics with question counts, without loading the questions."""
    question_count = (
        select(func.count(Question.id)).where(Question.topic_id == Topic.id).scalar_subquery()
    )
    query = select(Topic, question_count).where(Topic.set_id == set_id).order_by(Topic.position)

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def get_topic_with_questions(topic_id: uuid.UUID) -> tuple[QuestionSet, Topic] | None:
    query = (
        select(QuestionSet, Topic)
        .join(Topic, Topic.set_id == QuestionSet.id)
        .where(Topic.id == topic_id)
        .options(selectinload(Topic.questions))
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def get_for_question(question_id: uuid.UUID) -> QuestionSet | None:
    query = (
        select(QuestionSet)
        .join(Topic, Topic.set_id == QuestionSet.id)
        .join(Question, Question.topic_id == Topic.id)
        .where(Question.id == question_id)
    )

    async with Session() as session:
        return await session.scalar(query)


async def get_question_context(
    question_id: uuid.UUID,
) -> tuple[QuestionSet, Topic] | None:
    """The question's set and topic, with every question of that topic."""
    query = (
        select(QuestionSet, Topic)
        .join(Topic, Topic.set_id == QuestionSet.id)
        .join(Question, Question.topic_id == Topic.id)
        .where(Question.id == question_id)
        .options(selectinload(Topic.questions))
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def replace_question(
    question_id: uuid.UUID, text: str, reference_answer: str, options: list[dict]
) -> None:
    """New content in the same slot; feedback on the old question no longer applies."""
    async with Session() as session:
        await session.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(text=text, reference_answer=reference_answer, options=options)
        )
        await session.execute(delete(QuestionRating).where(QuestionRating.question_id == question_id))
        await session.execute(delete(QuestionReport).where(QuestionReport.question_id == question_id))
        await session.commit()


async def set_topic_limit(topic_id: uuid.UUID, limit: int | None) -> None:
    async with Session() as session:
        await session.execute(
            update(Topic).where(Topic.id == topic_id).values(question_limit=limit)
        )
        await session.commit()


async def set_title(set_id: uuid.UUID, title: str) -> None:
    async with Session() as session:
        await session.execute(
            update(QuestionSet).where(QuestionSet.id == set_id).values(title=title)
        )
        await session.commit()


async def set_visibility(set_id: uuid.UUID, visibility: str) -> None:
    async with Session() as session:
        await session.execute(
            update(QuestionSet).where(QuestionSet.id == set_id).values(visibility=visibility)
        )
        await session.commit()
