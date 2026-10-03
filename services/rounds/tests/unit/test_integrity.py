import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from prepza_common.auth import current_user
from prepza_common.user import User

from app.helpers.review import add_signals, build_review
from app.main import app
from app.models.rounds import Answer
from app.models.sessions import Session
from app.models.signals import Signal
from app.schemas.library import TopicQuestions
from app.storage import sessions

QUESTION_ID = uuid4()


def session(seconds):
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=uuid4(),
        topic_title="Python",
        status="in_progress",
        questions=[
            {
                "id": str(QUESTION_ID),
                "text": "Q?",
                "options": [{"answer": "A", "correct": True}, {"answer": "B", "correct": False}],
            }
        ],
        final_score=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        question_seconds=None,
        question_shown_at=None,
        answers=[
            Answer(
                id=uuid4(),
                question_id=QUESTION_ID,
                option_index=0,
                correct=True,
                score=100,
                seconds=seconds,
            )
        ],
    )


def test_answers_under_three_seconds_are_fast():
    assert build_review(session(seconds=2))[0].answer.fast
    assert not build_review(session(seconds=3))[0].answer.fast


def test_each_candidate_gets_their_own_option_order(monkeypatch):
    class FakeDb:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def add_all(self, rows):
            pass

        async def commit(self):
            pass

    monkeypatch.setattr(sessions, "Db", FakeDb)
    options = [{"answer": str(i), "correct": i == 0} for i in range(4)]
    topic = TopicQuestions.model_validate(
        {
            "id": str(uuid4()),
            "preparation_id": str(uuid4()),
            "title": "T",
            "questions": [{"id": str(uuid4()), "text": "Q?", "options": options}],
        }
    )
    orders = set()

    for _ in range(30):
        rows = asyncio.run(sessions.create_many("cand", uuid4(), [topic], 60))
        question = rows[0].questions[0]
        orders.add(tuple(option["answer"] for option in question["options"]))
        assert [option["answer"] for option in question["options"] if option["correct"]] == ["0"]

    assert len(orders) > 1


def test_the_browser_reports_signals(monkeypatch):
    row = session(seconds=10)
    row.answers = []
    row.question_shown_at = datetime.now(UTC)
    counted = []

    async def fake_get(session_id):
        return row

    async def fake_add_signal(session_id, question_id, kind):
        counted.append((question_id, kind))

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "add_signal", fake_add_signal)
    app.dependency_overrides[current_user] = lambda: User(
        uid="cand", email="cand@example.com", email_verified=True
    )

    try:
        client = TestClient(app)
        ok = client.post(f"/sessions/{row.id}/signals", json={"kind": "tab_leave"})
        bad = client.post(f"/sessions/{row.id}/signals", json={"kind": "other"})
    finally:
        app.dependency_overrides.clear()

    assert ok.status_code == 204
    assert bad.status_code == 422
    assert counted == [(QUESTION_ID, "tab_leave")]


def test_signals_are_counted_on_their_question():
    items = build_review(session(seconds=10))
    signals = [
        Signal(question_id=QUESTION_ID, kind="tab_leave"),
        Signal(question_id=QUESTION_ID, kind="tab_leave"),
        Signal(question_id=QUESTION_ID, kind="copy"),
        Signal(question_id=None, kind="tab_leave"),
    ]

    add_signals(items, signals)

    assert (items[0].tab_leaves, items[0].copies) == (2, 1)
