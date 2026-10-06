import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from prepza_common.user import User

from app.integrations import library
from app.models.answers import Answer
from app.models.sessions import Session
from app.services import interview_flow
from app.storage import sessions

CANDIDATE = User(uid="cand", email="cand@example.com", email_verified=True)
INVITE_ID = uuid4()


def section(answered=False, status="in_progress"):
    """A section with one question, answered or not."""
    question_id = uuid4()

    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=INVITE_ID,
        topic_title="Python",
        status=status,
        questions=[{"id": str(question_id), "text": "Q?", "options": [{"answer": "A"}]}],
        final_score=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        question_seconds=30,
        question_shown_at=None,
        answers=[Answer(question_id=question_id, option_index=0, score=100)] if answered else [],
    )


@pytest.fixture
def interview(monkeypatch):
    """Fakes the storage of one candidate's interview made of the sections a test passes."""
    rows = []
    finished = []

    async def fake_get(session_id):
        return next(row for row in rows if row.id == session_id)

    async def fake_list(invite_id):
        return rows

    async def fake_finish(session_id):
        finished.append(session_id)
        (await fake_get(session_id)).status = "finished"

    async def fake_shown(session_id):
        return datetime.now(UTC)

    async def no_library(set_id):
        return None

    async def nothing():
        return None

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "list_for_invite", fake_list)
    monkeypatch.setattr(sessions, "finish", fake_finish)
    monkeypatch.setattr(sessions, "mark_shown", fake_shown)
    monkeypatch.setattr(library, "get_set", no_library)
    monkeypatch.setattr(interview_flow.outbox_service, "flush_quietly", nothing)

    return rows, finished


def test_a_section_with_no_question_left_finishes_and_the_next_opens(interview):
    rows, finished = interview
    first, second = section(answered=True), section()
    rows += [first, second]

    step = asyncio.run(interview_flow.interview_step(first, CANDIDATE))

    assert finished == [first.id]
    assert step.session.id == second.id
    assert step.question is not None and step.question.seconds_left == pytest.approx(30, abs=1)
    assert step.done is False


def test_the_last_answer_finishes_the_interview(interview):
    rows, finished = interview
    first, last = section(answered=True, status="finished"), section(answered=True)
    rows += [first, last]

    step = asyncio.run(interview_flow.interview_step(last, CANDIDATE))

    assert finished == [last.id]
    assert step.question is None
    assert step.done is True


def test_finishing_the_interview_ends_every_open_section(interview):
    rows, finished = interview
    rows += [section(answered=True), section()]

    step = asyncio.run(interview_flow.finish_interview(rows[0], CANDIDATE))

    assert finished == [rows[0].id, rows[1].id]
    assert step.done is True
    assert [topic.status for topic in step.topics] == ["finished", "finished"]
