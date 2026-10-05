import uuid

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import QuestionRating, QuestionReport
from app.models.outbox import OutboxEvent
from app.models.quality import QuestionRevision, QuestionStats
from app.models.sets import Question
from app.storage.db import Session

# Counts one answer. Only when the question still has the text that was answered: an answer
# to a question since re-generated belongs to its old content, not the new one.
RECORD_ANSWER_SQL = text(
    """
    INSERT INTO question_stats (question_id, answers, correct, option_picks, updated_at)
    SELECT id, 1, CAST(:correct AS integer), jsonb_build_object(CAST(:option AS text), 1), now()
    FROM questions
    WHERE id = :question_id AND text = :question_text
    ON CONFLICT (question_id) DO UPDATE SET
        answers = question_stats.answers + 1,
        correct = question_stats.correct + EXCLUDED.correct,
        option_picks = question_stats.option_picks || jsonb_build_object(
            CAST(:option AS text),
            coalesce((question_stats.option_picks ->> CAST(:option AS text))::int, 0) + 1
        ),
        updated_at = now()
    """
)


async def record_answer(
    question_id: uuid.UUID, question_text: str, option: str, correct: bool
) -> None:
    async with Session() as session:
        await session.execute(
            RECORD_ANSWER_SQL,
            {
                "question_id": question_id,
                "question_text": question_text,
                "option": option,
                "correct": int(correct),
            },
        )
        await session.commit()


RECORD_RESULT_SQL = text(
    """
    INSERT INTO question_stats (
        question_id, answers, correct, option_picks, updated_at,
        strong_answers, strong_correct, weak_answers, weak_correct, timeouts
    )
    SELECT id, 0, 0, '{}'::jsonb, now(),
        CAST(:strong AS integer), CAST(:strong_correct AS integer),
        CAST(:weak AS integer), CAST(:weak_correct AS integer), CAST(:timed_out AS integer)
    FROM questions
    WHERE id = :question_id AND text = :question_text
    ON CONFLICT (question_id) DO UPDATE SET
        strong_answers = question_stats.strong_answers + EXCLUDED.strong_answers,
        strong_correct = question_stats.strong_correct + EXCLUDED.strong_correct,
        weak_answers = question_stats.weak_answers + EXCLUDED.weak_answers,
        weak_correct = question_stats.weak_correct + EXCLUDED.weak_correct,
        timeouts = question_stats.timeouts + EXCLUDED.timeouts,
        updated_at = now()
    """
)


async def record_result(
    question_id: uuid.UUID,
    question_text: str,
    group: str | None,
    correct: bool,
    timed_out: bool,
) -> None:
    """Counts one candidate's result on the question: in the strong or weak group (None: in
    between, not counted there), and whether their time ran out."""
    async with Session() as session:
        await session.execute(
            RECORD_RESULT_SQL,
            {
                "question_id": question_id,
                "question_text": question_text,
                "strong": int(group == "strong"),
                "strong_correct": int(group == "strong" and correct),
                "weak": int(group == "weak"),
                "weak_correct": int(group == "weak" and correct),
                "timed_out": int(timed_out),
            },
        )
        await session.commit()


async def source_of(question_id: uuid.UUID) -> uuid.UUID | None:
    """The bank question a test's question was copied from, if any."""
    async with Session() as session:
        return await session.scalar(
            select(Question.source_question_id).where(Question.id == question_id)
        )


async def rating_counts(session: AsyncSession, question_id: uuid.UUID) -> tuple[int, int]:
    """Likes and dislikes."""
    query = select(
        func.count().filter(QuestionRating.value == 1),
        func.count().filter(QuestionRating.value == -1),
    ).where(QuestionRating.question_id == question_id)

    return tuple((await session.execute(query)).one())


async def load(
    question_id: uuid.UUID,
) -> tuple[Question, QuestionStats | None, dict[str, int], int, int] | None:
    """The question, its answer stats, report counts per reason, likes and dislikes."""
    reports = (
        select(QuestionReport.reason, func.count())
        .where(QuestionReport.question_id == question_id)
        .group_by(QuestionReport.reason)
    )

    async with Session() as session:
        question = await session.get(Question, question_id)

        if question is None:
            return None

        stats = await session.get(QuestionStats, question_id)
        likes, dislikes = await rating_counts(session, question_id)

        return (
            question,
            stats,
            dict((await session.execute(reports)).all()),
            likes,
            dislikes,
        )


async def save_flag(
    question_id: uuid.UUID, flag: str | None, kept: bool = False, notice: dict | None = None
) -> None:
    """Also for a question nobody has answered yet: reports alone can flag it. `notice` is the
    owner's notification, saved with the flag."""
    statement = (
        insert(QuestionStats)
        .values(
            question_id=question_id,
            answers=0,
            correct=0,
            option_picks={},
            flag=flag,
            kept=kept,
        )
        .on_conflict_do_update(
            index_elements=[QuestionStats.question_id],
            set_={"flag": flag, "kept": kept},
        )
    )

    async with Session() as session:
        await session.execute(statement)

        if notice is not None:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        await session.commit()


async def archive(session: AsyncSession, question_id: uuid.UUID) -> None:
    """Moves a question's content, answer stats and feedback into a revision, in `session`.

    The caller then replaces the question; its new content starts with no feedback.
    """
    question = await session.get(Question, question_id)

    if question is None:
        return

    stats = await session.get(QuestionStats, question_id)
    likes, dislikes = await rating_counts(session, question_id)
    reports = await session.scalars(
        select(QuestionReport).where(QuestionReport.question_id == question_id)
    )
    session.add(
        QuestionRevision(
            question_id=question_id,
            text=question.text,
            options=question.options,
            answers=stats.answers if stats else 0,
            correct=stats.correct if stats else 0,
            option_picks=stats.option_picks if stats else {},
            likes=likes,
            dislikes=dislikes,
            reports=[
                {
                    "reason": report.reason,
                    "comment": report.comment,
                    "created_at": report.created_at.isoformat(),
                }
                for report in reports
            ],
        )
    )

    for model in (QuestionStats, QuestionRating, QuestionReport):
        await session.execute(delete(model).where(model.question_id == question_id))
