from datetime import UTC, datetime
from uuid import uuid4

from app.helpers.sessions import session_out, topic_out
from app.models.sessions import Session


def session(answers=None, final=80):
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=uuid4(),
        topic_title="Python",
        status="finished",
        questions=[{}, {}],
        final_score=final,
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        answers=answers or [],
    )


def test_candidates_never_see_their_scores():
    shown = session_out(session()).model_dump()

    assert "final_score" not in shown
    assert "current_score" not in shown
    assert "passed" not in shown


def test_topic_out_counts_questions():
    row = session()
    topic = topic_out(row)

    assert topic.topic_title == "Python"
    assert topic.total == 2
    assert topic.answered == 0
