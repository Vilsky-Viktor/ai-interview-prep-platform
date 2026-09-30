from app.helpers.scores import (
    candidate_progress,
    clamp_score,
    current_score,
    final_score,
    interview_finished,
)


def test_current_score_is_average_of_answered():
    assert current_score([]) is None
    assert current_score([100, 0, 50]) == 50


def test_choice_final_score_counts_unanswered_as_wrong():
    assert final_score("choice", [100, 100, 0], 10) == 20


def test_open_final_score_is_average_grade():
    assert final_score("open", [90, 80], 10) == 85
    assert final_score("open", [], 10) == 0


def test_candidate_progress_splits_completion_and_grade():
    assert candidate_progress([], 10) == (0, None)
    assert candidate_progress([100, 0], 10) == (20, 50)
    assert candidate_progress([90, 70], 4) == (50, 80)


def test_interview_finished_needs_every_topic():
    assert interview_finished([]) is False
    assert interview_finished(["finished", "in_progress"]) is False
    assert interview_finished(["finished", "finished"]) is True


def test_clamp_score():
    assert clamp_score(120) == 100
    assert clamp_score(-5) == 0
