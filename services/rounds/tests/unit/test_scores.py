from app.helpers.scores import final_score, interview_finished, invite_grade


def test_final_score_counts_unanswered_as_wrong():
    assert final_score([100, 100, 0], 10) == 20
    assert final_score([], 10) == 0
    assert final_score([], 0) == 0


def test_invite_grade_splits_completion_and_score():
    assert invite_grade(0, 0, 10, False) == {"progress": 0, "grade": None, "finished": False}
    # Two of ten answered, one right: 50% so far.
    assert invite_grade(2, 100, 10, False) == {"progress": 20, "grade": 50, "finished": False}
    # Once finished, the eight never answered count as wrong.
    assert invite_grade(2, 100, 10, True) == {"progress": 20, "grade": 10, "finished": True}


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


def test_only_the_same_question_with_the_same_options_is_rekeyed():
    from app.helpers.rescore import rekeyed

    def copy():
        return {
            "text": "Q?",
            "options": [{"answer": "b", "correct": True}, {"answer": "a", "correct": False}],
        }

    fixed = [{"answer": "a", "correct": True}, {"answer": "b", "correct": False}]
    question = copy()

    assert rekeyed(question, "Q?", fixed)
    # The candidate's option order stays; only the key moves.
    assert question["options"] == [
        {"answer": "b", "correct": False},
        {"answer": "a", "correct": True},
    ]
    assert not rekeyed(copy(), "Other?", fixed)
    assert not rekeyed(copy(), "Q?", [{"answer": "c", "correct": True}])
