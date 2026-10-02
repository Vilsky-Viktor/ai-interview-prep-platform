import uuid

from prepza_common.sets import PreparationIn
from sqlalchemy import Row, delete, func, select, update
from sqlalchemy.orm import selectinload

from app.constants.sets import OwnerType, SetKind, Visibility
from app.models.sets import Question, QuestionSet, Topic
from app.models.sharing import JoinedPreparation
from app.storage import quality, reuse
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
                    options=[option.model_dump() for option in question.options],
                )
                for qi, question in enumerate(topic.questions)
            ],
        )
        for ti, topic in enumerate(preparation.topics)
    ]


async def find_by_generation(generation_id: uuid.UUID) -> uuid.UUID | None:
    query = select(QuestionSet.id).where(QuestionSet.generation_id == generation_id)

    async with Session() as session:
        return await session.scalar(query)


async def create(preparation: PreparationIn) -> uuid.UUID:
    question_set = QuestionSet(
        generation_id=preparation.generation_id,
        kind=SetKind.PREPARATION,
        owner_type=OwnerType.USER,
        owner_id=preparation.owner_uid,
        title=preparation.title,
        source_text=preparation.source_text,
        level=preparation.level,
        requirements=preparation.requirements,
        topics=_topics(preparation),
        topic_count=len(preparation.topics),
        join_count=1,
    )

    async with Session() as session:
        session.add(question_set)
        await session.flush()
        session.add(
            JoinedPreparation(set_id=question_set.id, user_id=preparation.owner_uid)
        )
        await reuse.save_embeddings(
            session,
            [topic.id for topic in question_set.topics],
            [topic.embedding for topic in preparation.topics],
        )
        await session.commit()

    return question_set.id


async def create_interview(payload: PreparationIn) -> uuid.UUID:
    """Company interviews are always private."""
    question_set = QuestionSet(
        generation_id=payload.generation_id,
        kind=SetKind.INTERVIEW,
        owner_type=OwnerType.COMPANY,
        owner_id=payload.owner_uid,
        title=payload.title,
        source_text=payload.source_text,
        level=payload.level,
        requirements=payload.requirements,
        visibility=Visibility.PRIVATE,
        topics=_topics(payload),
        topic_count=len(payload.topics),
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


async def list_mine(user_id: str, offset: int, limit: int) -> list[Row]:
    """Preparations the user owns or joined (owners are joined to their own), newest first."""
    query = (
        select(QuestionSet, *summary_columns())
        .join(JoinedPreparation, JoinedPreparation.set_id == QuestionSet.id)
        .where(JoinedPreparation.user_id == user_id, QuestionSet.kind == SetKind.PREPARATION)
        .order_by(QuestionSet.created_at.desc(), QuestionSet.id)
        .offset(offset)
        .limit(limit)
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


async def get_topic_with_question_texts(
    topic_id: uuid.UUID,
) -> tuple[QuestionSet, Topic] | None:
    """Like get_topic_with_questions, but its questions carry only their id and text."""
    query = (
        select(QuestionSet, Topic)
        .join(Topic, Topic.set_id == QuestionSet.id)
        .where(Topic.id == topic_id)
        .options(selectinload(Topic.questions).load_only(Question.id, Question.text))
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


async def replace_question(question_id: uuid.UUID, text: str, options: list[dict]) -> None:
    """New content in the same slot. The old content and its feedback are kept as a revision."""
    async with Session() as session:
        await quality.archive(session, question_id)
        await session.execute(
            update(Question).where(Question.id == question_id).values(text=text, options=options)
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


async def remove(set_id: uuid.UUID) -> None:
    """Deletes the set; its topics, questions, feedback, invites and joins cascade with it."""
    async with Session() as session:
        await session.execute(delete(QuestionSet).where(QuestionSet.id == set_id))
        await session.commit()
