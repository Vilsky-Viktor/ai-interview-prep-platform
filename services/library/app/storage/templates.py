import uuid

from prepza_common.sets import PreparationIn
from sqlalchemy import Text, cast, or_, select
from sqlalchemy.orm import selectinload

from app.constants.sets import PLATFORM_OWNER, REVEALED_EVERY, OwnerType, SetKind, Stage
from app.helpers.search import escape_like
from app.models.sets import Question, QuestionSet, Topic
from app.storage import reuse
from app.storage.db import Session
from app.storage.preparations import new_topics


async def create_template(payload: PreparationIn) -> uuid.UUID:
    """An admin's template, with its topics' embeddings for the question bank."""
    question_set = QuestionSet(
        generation_id=payload.generation_id,
        kind=SetKind.TEMPLATE,
        owner_type=OwnerType.PLATFORM,
        owner_id=PLATFORM_OWNER,
        title=payload.title,
        source_text=payload.source_text,
        level=payload.level,
        language=payload.language,
        requirements=payload.requirements,
        topics=new_topics(payload),
        topic_count=len(payload.topics),
    )

    # About a third of each topic goes straight to practice; the rest start private.
    for topic in question_set.topics:
        for question in topic.questions:
            if question.position % REVEALED_EVERY == REVEALED_EVERY - 1:
                question.stage = Stage.REVEALED

    async with Session() as session:
        session.add(question_set)
        await session.flush()
        await reuse.save_embeddings(
            session,
            [topic.id for topic in question_set.topics],
            [topic.embedding for topic in payload.topics],
        )
        await session.commit()

    return question_set.id


async def copy_template(template_id: uuid.UUID, company_id: str) -> QuestionSet | None:
    """A company's own test made from a template, with no generation: its topics and their
    private questions, each remembering its original so its answers count there too. None when
    there's no such template."""
    query = (
        select(QuestionSet)
        .where(QuestionSet.id == template_id, QuestionSet.kind == SetKind.TEMPLATE)
        .options(selectinload(QuestionSet.topics).selectinload(Topic.questions))
    )

    async with Session() as session:
        template = await session.scalar(query)

        if template is None:
            return None

        copy = QuestionSet(
            kind=SetKind.INTERVIEW,
            owner_type=OwnerType.COMPANY,
            owner_id=company_id,
            title=template.title,
            source_text=template.source_text,
            level=template.level,
            language=template.language,
            requirements=template.requirements,
            topic_count=template.topic_count,
            topics=[
                Topic(
                    position=topic.position,
                    title=topic.title,
                    subtopics=topic.subtopics,
                    questions=[
                        Question(
                            position=q.position,
                            text=q.text,
                            options=q.options,
                            source_question_id=q.id,
                        )
                        for q in topic.questions
                        if q.stage == Stage.PRIVATE
                    ],
                )
                for topic in template.topics
            ],
        )
        session.add(copy)
        await session.commit()

        return copy


async def list_templates(
    q: str, level: str | None, languages: list[str], offset: int, limit: int
) -> list[QuestionSet]:
    """Newest first; `q` matches anywhere in the title, a topic's title or a subtopic, and no
    languages means every one."""
    filters = [QuestionSet.kind == SetKind.TEMPLATE]

    if q:
        pattern = f"%{escape_like(q)}%"
        in_topics = (
            select(Topic.id)
            .where(
                Topic.set_id == QuestionSet.id,
                or_(
                    Topic.title.ilike(pattern, escape="\\"),
                    cast(Topic.subtopics, Text).ilike(pattern, escape="\\"),
                ),
            )
            .exists()
        )
        filters.append(or_(QuestionSet.title.ilike(pattern, escape="\\"), in_topics))

    if level:
        filters.append(QuestionSet.level == level)

    if languages:
        filters.append(QuestionSet.language.in_(languages))

    query = (
        select(QuestionSet)
        .where(*filters)
        .order_by(QuestionSet.created_at.desc(), QuestionSet.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))
