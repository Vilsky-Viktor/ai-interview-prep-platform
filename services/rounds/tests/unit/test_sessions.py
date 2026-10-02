from datetime import UTC, datetime
from uuid import uuid4

from app.helpers.sessions import session_out, topic_out
from app.models.sessions import Session


def session(share_results, answers=None, final=80):
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=uuid4(),
        topic_title="Python",
        share_results=share_results,
        status="finished",
        questions=[{}, {}],
        final_score=final,
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        answers=answers or [],
    )


def test_session_hides_scores_unless_shared():
    hidden = session_out(session(False))
    shown = session_out(session(True))

    assert hidden.final_score is None
    assert hidden.current_score is None
    assert shown.final_score == 80


def test_topic_out_counts_questions():
    row = session(True)
    topic = topic_out(row)

    assert topic.topic_title == "Python"
    assert topic.total == 2
    assert topic.answered == 0
