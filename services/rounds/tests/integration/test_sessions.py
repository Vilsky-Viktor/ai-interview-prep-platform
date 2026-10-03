import asyncio
import uuid

from app.models.rounds import Answer
from app.storage import sessions
from tests.integration.factories import topic


def timed_out(session_id, question_id):
    return Answer(
        session_id=session_id,
        question_id=question_id,
        option_index=None,
        correct=False,
        score=0,
        seconds=30,
    )


def test_two_requests_timing_out_the_same_question_save_one_answer(run):
    async def scenario():
        [row] = await sessions.create_many("cand", uuid.uuid4(), [topic()], 30)
        await sessions.mark_shown(row.id)
        question_id = uuid.UUID(row.questions[0]["id"])
        saved = await asyncio.gather(
            sessions.add_answer(timed_out(row.id, question_id)),
            sessions.add_answer(timed_out(row.id, question_id)),
        )

        return saved, await sessions.get(row.id)

    saved, row = run(scenario())

    assert sorted(saved) == [False, True]
    assert len(row.answers) == 1
    # The answer stopped the clock, so the next question starts its own.
    assert row.question_shown_at is None


def test_signals_are_saved_with_their_question_and_loaded_with_the_session(run):
    invite_id = uuid.uuid4()

    async def scenario():
        [row] = await sessions.create_many("cand", invite_id, [topic()], 60)
        question_id = uuid.UUID(row.questions[0]["id"])
        await sessions.add_signal(row.id, question_id, "tab_leave")
        await sessions.add_signal(row.id, None, "copy")

        return await sessions.list_for_invite(invite_id), question_id

    [row], question_id = run(scenario())

    assert sorted((signal.kind, signal.question_id) for signal in row.signals) == [
        ("copy", None),
        ("tab_leave", question_id),
    ]


def test_scores_show_progress_and_the_grade_of_answers_so_far(run):
    invite_id = uuid.uuid4()

    async def scenario():
        rows = await sessions.create_many("cand", invite_id, [topic(4)], 60)
        row = rows[0]
        question = row.questions[0]
        correct = next(i for i, option in enumerate(question["options"]) if option["correct"])
        await sessions.add_answer(
            Answer(
                session_id=row.id,
                question_id=uuid.UUID(question["id"]),
                option_index=correct,
                correct=True,
                score=100,
            )
        )

        return await sessions.scores_for_invites([invite_id])

    progress, grade, finished = run(scenario())[invite_id]

    # One of four answered, and right: 25% through, 100% correct so far. Unanswered questions
    # count as wrong only in the final score, once the interview ends.
    assert (progress, grade, finished) == (25, 100, False)
