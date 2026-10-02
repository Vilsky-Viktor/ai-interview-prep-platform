import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.helpers.review import build_review
from app.helpers.sessions import answer_seconds
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.services import session_answers
from app.storage import sessions

QUESTION_ID = uuid4()


def session(shown_at):
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=uuid4(),
        topic_title="Python",
        share_results=False,
        status="in_progress",
        questions=[
            {
                "id": str(QUESTION_ID),
                "text": "Q?",
                "options": [
                    {"answer": "Right", "correct": True},
                    {"answer": "Wrong", "correct": False},
                ],
            }
        ],
        final_score=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        question_seconds=None,
        question_shown_at=shown_at,
        answers=[],
    )


def test_answer_seconds():
    shown = datetime(2026, 10, 2, 12, 0, 0, tzinfo=UTC)

    assert answer_seconds(shown, shown + timedelta(seconds=12.4)) == 12
    assert answer_seconds(None, shown) is None


def test_answer_records_the_seconds_since_the_question_was_shown(monkeypatch):
    saved = []

    async def fake_add(answer):
        answer.id = uuid4()
        saved.append(answer)

        return True

    async def no_announce(answer, question):
        return None

    monkeypatch.setattr(sessions, "add_answer", fake_add)
    monkeypatch.setattr(session_answers, "announce", no_announce)
    row = session(datetime.now(UTC) - timedelta(seconds=30))

    asyncio.run(
        session_answers.submit_session_answer(
            row, AnswerCreate(question_id=QUESTION_ID, option_index=0)
        )
    )

    assert 29 <= saved[0].seconds <= 31
    row.answers = saved
    assert build_review(row)[0].answer.seconds == saved[0].seconds
