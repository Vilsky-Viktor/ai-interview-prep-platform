import uuid

from sqlalchemy import bindparam, delete, select, text

from app.models.progress import QuestionProgress
from app.storage.db import Session

# Per user, question and mode: the answer from the latest finished round, with the question
# text that round asked.
REBUILD_SQL = text(
    """
    INSERT INTO question_progress
        (user_id, question_id, mode, preparation_id, topic_id, question_text, score, answered_at)
    SELECT DISTINCT ON (rounds.user_id, answers.question_id, rounds.mode)
        rounds.user_id, answers.question_id, rounds.mode, rounds.preparation_id,
        rounds.topic_id, asked->>'text', answers.score, rounds.finished_at
    FROM rounds
    JOIN answers ON answers.round_id = rounds.id
    CROSS JOIN LATERAL jsonb_array_elements(rounds.questions) AS asked
    WHERE rounds.user_id = :user_id
      AND rounds.status = 'finished'
      AND answers.question_id IN :question_ids
      AND asked->>'id' = answers.question_id::text
    ORDER BY rounds.user_id, answers.question_id, rounds.mode, rounds.started_at DESC
    """
).bindparams(bindparam("question_ids", expanding=True))


async def rebuild(user_id: str, question_ids: list[uuid.UUID]) -> None:
    """Recomputes the user's progress on these questions after a round finished or was deleted."""
    if not question_ids:
        return

    async with Session() as session:
        await session.execute(
            delete(QuestionProgress).where(
                QuestionProgress.user_id == user_id,
                QuestionProgress.question_id.in_(question_ids),
            )
        )
        await session.execute(REBUILD_SQL, {"user_id": user_id, "question_ids": question_ids})
        await session.commit()


async def for_topic(user_id: str, topic_id: uuid.UUID, mode: str) -> list[QuestionProgress]:
    query = select(QuestionProgress).where(
        QuestionProgress.user_id == user_id,
        QuestionProgress.topic_id == topic_id,
        QuestionProgress.mode == mode,
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def for_preparation(user_id: str, preparation_id: uuid.UUID) -> list[QuestionProgress]:
    query = select(QuestionProgress).where(
        QuestionProgress.user_id == user_id,
        QuestionProgress.preparation_id == preparation_id,
    )

    async with Session() as session:
        return list(await session.scalars(query))
