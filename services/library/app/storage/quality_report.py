from sqlalchemy import func, select

from app.models.feedback import QuestionReport
from app.models.quality import QuestionRevision, QuestionStats
from app.models.sets import Question, QuestionSet, Topic
from app.storage.db import Session


async def flagged(offset: int, limit: int) -> list:
    """Questions flagged now, newest first, with their set and statistics."""
    reports = (
        select(func.count()).where(QuestionReport.question_id == Question.id).scalar_subquery()
    )
    query = (
        select(Question, QuestionStats, QuestionSet, reports.label("reports"))
        .join(QuestionStats, QuestionStats.question_id == Question.id)
        .join(Topic, Topic.id == Question.topic_id)
        .join(QuestionSet, QuestionSet.id == Topic.set_id)
        .where(QuestionStats.flag.is_not(None))
        .order_by(QuestionStats.updated_at.desc(), Question.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.execute(query))


async def replaced(offset: int, limit: int) -> list:
    """Questions the verifier or an owner replaced, newest first: the old content and its set."""
    query = (
        select(QuestionRevision, QuestionSet)
        .join(Question, Question.id == QuestionRevision.question_id)
        .join(Topic, Topic.id == Question.topic_id)
        .join(QuestionSet, QuestionSet.id == Topic.set_id)
        .order_by(QuestionRevision.replaced_at.desc(), QuestionRevision.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.execute(query))


async def revision(revision_id) -> QuestionRevision | None:
    async with Session() as session:
        return await session.get(QuestionRevision, revision_id)
