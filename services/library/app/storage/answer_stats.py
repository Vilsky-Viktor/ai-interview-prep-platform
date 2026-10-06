import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sets import Question
from app.storage import processed_events
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

# Counts one candidate's result on a question: in the strong or weak group (or neither), and
# whether their time ran out. Only for the text that was answered, as above.
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


async def with_sources(
    session: AsyncSession, question_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[uuid.UUID]]:
    """Each question with the bank question it was copied from, if any: an original's answers
    add up across every test that uses it. One query for them all."""
    rows = await session.execute(
        select(Question.id, Question.source_question_id).where(Question.id.in_(question_ids))
    )
    sources = dict(rows.all())

    return {
        question_id: [question_id] + ([sources[question_id]] if sources.get(question_id) else [])
        for question_id in question_ids
    }


async def record_answer(
    event_id: str, question_id: uuid.UUID, question_text: str, option: str, correct: bool
) -> list[uuid.UUID] | None:
    """Counts one answer for the question and its bank original, in one transaction and once
    per event. The questions counted, or None when the event was counted before."""
    async with Session() as session:
        if not await processed_events.claim(session, event_id):
            return None

        counted = (await with_sources(session, [question_id]))[question_id]

        for answered in counted:
            await session.execute(
                RECORD_ANSWER_SQL,
                {
                    "question_id": answered,
                    "question_text": question_text,
                    "option": option,
                    "correct": int(correct),
                },
            )

        await session.commit()

        return counted


async def record_results(
    event_id: str, group: str | None, results: list[dict]
) -> list[uuid.UUID] | None:
    """Counts one finished topic's results ({"question_id", "question_text", "correct",
    "timed_out"}) for each question and its bank original, in one transaction and once per
    event. `group` is the candidate's: strong, weak, or None in between (not counted there).
    The questions counted, or None when the event was counted before."""
    async with Session() as session:
        if not await processed_events.claim(session, event_id):
            return None

        ids = [uuid.UUID(result["question_id"]) for result in results]
        sources = await with_sources(session, ids)
        counted = []

        for question_id, result in zip(ids, results):
            for answered in sources[question_id]:
                await session.execute(
                    RECORD_RESULT_SQL,
                    {
                        "question_id": answered,
                        "question_text": result["question_text"],
                        "strong": int(group == "strong"),
                        "strong_correct": int(group == "strong" and result["correct"]),
                        "weak": int(group == "weak"),
                        "weak_correct": int(group == "weak" and result["correct"]),
                        "timed_out": int(result["timed_out"]),
                    },
                )
                counted.append(answered)

        await session.commit()

        return list(dict.fromkeys(counted))
