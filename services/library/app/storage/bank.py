from datetime import datetime

from sqlalchemy import text

from app.constants.reuse import RETIRE_AFTER_ANSWERS
from app.constants.sets import SetKind, Stage
from app.storage.db import Session

# Private template questions that have served enough candidates stop going into new tests.
RETIRE_SQL = text(
    """
    UPDATE questions q SET stage = :retiring
    FROM question_stats qs, topics t, sets s
    WHERE qs.question_id = q.id AND t.id = q.topic_id AND s.id = t.set_id
        AND s.kind = :template AND q.stage = :private AND qs.answers >= :retire_after
    """
)

# Retiring questions no test has used a copy of since `idle_since` (last answered, or added to a
# test) are revealed for practice.
REVEAL_SQL = text(
    """
    UPDATE questions q SET stage = :revealed
    WHERE q.stage = :retiring AND NOT EXISTS (
        SELECT 1 FROM questions c
        JOIN topics ct ON ct.id = c.topic_id
        JOIN sets cs ON cs.id = ct.set_id
        LEFT JOIN question_stats cqs ON cqs.question_id = c.id
        WHERE c.source_question_id = q.id
            AND coalesce(cqs.updated_at, cs.created_at) > :idle_since
    )
    """
)


async def move_stages(idle_since: datetime) -> tuple[int, int]:
    """Moves bank questions one stage forward where they're due; (retired, revealed)."""
    async with Session() as session:
        retired = await session.execute(
            RETIRE_SQL,
            {
                "retiring": Stage.RETIRING,
                "private": Stage.PRIVATE,
                "template": SetKind.TEMPLATE,
                "retire_after": RETIRE_AFTER_ANSWERS,
            },
        )
        revealed = await session.execute(
            REVEAL_SQL,
            {"revealed": Stage.REVEALED, "retiring": Stage.RETIRING, "idle_since": idle_since},
        )
        await session.commit()

        return retired.rowcount, revealed.rowcount
