import uuid

from prepza_common import outbox
from sqlalchemy import select
from sqlalchemy.orm import attributes, selectinload

from app.constants.events import RESULTS_RESCORED
from app.constants.rounds import CORRECT_SCORE, RoundStatus
from app.helpers.rescore import rekeyed
from app.helpers.scores import final_score
from app.models.outbox import OutboxEvent
from app.models.sessions import Session
from app.storage.db import Session as Db


async def rescore_question(
    question_id: uuid.UUID, text: str, options: list[dict], set_id: uuid.UUID | None = None
) -> int:
    """A question's answer key was corrected: every session that asked it, unchanged, marks its
    candidate's pick again, and a finished section's score follows; companies hears whose
    results changed, so it stores their new grades. Only the question's interview (`set_id`) is
    looked at when given. Returns how many sessions changed."""
    query = (
        select(Session)
        .where(Session.questions.contains([{"id": str(question_id)}]))
        .options(selectinload(Session.answers))
        .order_by(Session.id)
        .with_for_update(of=Session)
    )

    if set_id is not None:
        query = query.where(Session.interview_set_id == set_id)

    changed = 0
    rescored = set()

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
                rescored.add(str(row.candidate_invite_id))

        if rescored:
            outbox.add(
                db, OutboxEvent, RESULTS_RESCORED, {"candidate_invite_ids": sorted(rescored)}
            )

        await db.commit()

    return changed
