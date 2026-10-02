from app.helpers.scores import (
    candidate_progress,
    current_score,
    earns_certificate,
    final_score,
    interview_finished,
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


def test_certificate_needs_full_coverage_and_70_percent():
    assert earns_certificate(None) is False
    assert earns_certificate(69) is False
    assert earns_certificate(70) is True
