from types import SimpleNamespace as Row

from app.helpers.scores import (
    candidate_progress,
    current_score,
    final_score,
    interview_finished,
    signal_counts,
)


def test_current_score_is_percent_correct_of_answered():
    assert current_score([]) is None
    assert current_score([100, 0, 100, 100]) == 75


def test_final_score_counts_unanswered_as_wrong():
    assert final_score([100, 100, 0], 10) == 20
    assert final_score([], 10) == 0
    assert final_score([], 0) == 0


def test_candidate_progress_splits_completion_and_score():
    assert candidate_progress([], 10) == (0, None)
    assert candidate_progress([100, 0], 10) == (20, 50)
    assert candidate_progress([100, 100, 0, 100], 4) == (100, 75)


def test_interview_finished_needs_every_topic():
    assert interview_finished([]) is False
    assert interview_finished(["finished", "in_progress"]) is False
    assert interview_finished(["finished", "finished"]) is True


def test_a_finished_section_reports_each_shown_questions_result():
    from types import SimpleNamespace
    from uuid import uuid4

    from app.helpers.scores import scored

    answered, timed_out, unseen = uuid4(), uuid4(), uuid4()
    row = SimpleNamespace(
        final_score=50,
        questions=[
            {"id": str(answered), "text": "Q1?"},
            {"id": str(timed_out), "text": "Q2?"},
            {"id": str(unseen), "text": "Q3?"},
        ],
        answers=[
            SimpleNamespace(question_id=answered, option_index=1, correct=True),
            SimpleNamespace(question_id=timed_out, option_index=None, correct=False),
        ],
    )

    assert scored(row) == {
        "final_score": 50,
        "answers": [
            {
                "question_id": str(answered),
                "question_text": "Q1?",
                "correct": True,
                "timed_out": False,
            },
            {
                "question_id": str(timed_out),
                "question_text": "Q2?",
                "correct": False,
                "timed_out": True,
            },
        ],
    }


def test_signal_counts_add_up_every_section():
    def answer(option_index, seconds):
        return Row(option_index=option_index, seconds=seconds)

    first = Row(
        signals=[Row(kind="tab_leave"), Row(kind="tab_leave"), Row(kind="copy")],
        # Picked in 1 second: too fast. Timed out (nothing picked): not fast.
        answers=[answer(0, 1), answer(None, 0)],
    )
    second = Row(signals=[Row(kind="tab_leave")], answers=[answer(1, 20), answer(2, 2)])

    assert signal_counts([first, second]) == {"tab_leaves": 3, "copies": 1, "fast_answers": 2}
