import uuid

from sqlalchemy import select

from app.models.answers import Answer
from app.models.outbox import OutboxEvent
from app.storage import rescore, sessions
from app.storage.db import Session as Db
from tests.integration.factories import option_index, topic


def test_a_corrected_key_marks_past_answers_again_and_updates_finished_scores(run):
    async def scenario():
        [session] = await sessions.create_many("cand", uuid.uuid4(), [topic(size=2)], 60)
        question = session.questions[0]
        # The candidate picked "wrong", which the corrected key says is right.
        await sessions.add_answer(
            Answer(
                session_id=session.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, False),
                correct=False,
                score=0,
            ),
            ("answer.recorded", {"question_id": question["id"]}),
        )
        await sessions.finish(session.id)
        corrected = [{"answer": "right", "correct": False}, {"answer": "wrong", "correct": True}]
        changed = await rescore.rescore_question(question["id"], question["text"], corrected)
        # A rewritten question was a different question: its answers stay as they were.
        rewritten = await rescore.rescore_question(question["id"], "Another question?", corrected)

        return changed, rewritten, await sessions.get(session.id)

    changed, rewritten, after = run(scenario())

    assert (changed, rewritten) == (1, 0)
    [answer] = after.answers
    assert answer.correct is True and answer.score == 100
    # One of two questions right.
    assert after.final_score == 50


def test_a_rescore_looks_only_at_the_questions_interview_and_tells_companies(run):
    async def scenario():
        invite_id = uuid.uuid4()
        [session] = await sessions.create_many("cand", invite_id, [topic(size=1)], 60)
        question = session.questions[0]
        await sessions.add_answer(
            Answer(
                session_id=session.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, False),
                correct=False,
                score=0,
            )
        )
        await sessions.finish(session.id)
        corrected = [{"answer": "right", "correct": False}, {"answer": "wrong", "correct": True}]
        elsewhere = await rescore.rescore_question(
            question["id"], question["text"], corrected, uuid.uuid4()
        )
        changed = await rescore.rescore_question(
            question["id"], question["text"], corrected, session.interview_set_id
        )

        async with Db() as db:
            events = list(
                await db.scalars(
                    select(OutboxEvent.data).where(OutboxEvent.event_type == "results.rescored")
                )
            )

        return elsewhere, changed, events, invite_id

    elsewhere, changed, events, invite_id = run(scenario())

    assert (elsewhere, changed) == (0, 1)
    assert {"candidate_invite_ids": [str(invite_id)]} in events
