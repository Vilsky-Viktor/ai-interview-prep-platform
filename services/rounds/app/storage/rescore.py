import uuid

from sqlalchemy import select
from sqlalchemy.orm import attributes, selectinload

from app.constants.rounds import CORRECT_SCORE, RoundStatus
from app.helpers.rescore import rekeyed
from app.helpers.scores import final_score
from app.models.sessions import Session
from app.storage.db import Session as Db


async def rescore_question(question_id: uuid.UUID, text: str, options: list[dict]) -> int:
    """A question's answer key was corrected: every session that asked it, unchanged, marks its
    candidate's pick again, and a finished section's score follows. Returns how many sessions
    changed."""
    query = (
        select(Session)
        .where(Session.questions.contains([{"id": str(question_id)}]))
        .options(selectinload(Session.answers))
        .with_for_update(of=Session)
    )
    changed = 0

    async with Db() as db:
        for row in await db.scalars(query):
            question = next(item for item in row.questions if item["id"] == str(question_id))

            if not rekeyed(question, text, options):
                continue

            attributes.flag_modified(row, "questions")
            changed += 1

            for answer in row.answers:
                if str(answer.question_id) == str(question_id) and answer.option_index is not None:
                    answer.correct = question["options"][answer.option_index]["correct"]
                    answer.score = CORRECT_SCORE if answer.correct else 0

            if row.status == RoundStatus.FINISHED:
                row.final_score = final_score(
                    [answer.score for answer in row.answers], len(row.questions)
                )

        await db.commit()

    return changed
