import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from prepza_common.user import User

from app.constants.rounds import TIME_UP
from app.models.rounds import Answer
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.service_auth import service_token
from app.services.session_access import get_owned_session
from app.services.session_answers import submit_session_answer
from app.storage import sessions

CANDIDATE = User(uid="cand", email="cand@example.com", email_verified=True)
INVITE_ID = uuid4()
QUESTION_ID = uuid4()


def timed(shown_seconds_ago, answers=None):
    """A section whose question has 30 seconds and was shown this many seconds ago."""
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=INVITE_ID,
        topic_title="Python",
        share_results=False,
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
        question_seconds=30,
        question_shown_at=datetime.now(UTC) - timedelta(seconds=shown_seconds_ago),
        answers=answers or [],
    )


def test_starting_a_timed_interview_passes_the_seconds_per_question(client, monkeypatch):
    created = {}

    async def no_sessions(invite_id):
        return []

    async def fake_create(user_id, invite_id, share_results, topics, question_seconds):
        created["question_seconds"] = question_seconds

        return []

    monkeypatch.setattr(sessions, "list_for_invite", no_sessions)
    monkeypatch.setattr(sessions, "create_many", fake_create)
    body = {
        "user_id": "cand",
        "candidate_invite_id": str(INVITE_ID),
        "share_results": False,
        "topics": [],
        "question_seconds": 45,
    }

    response = client.post(
        "/internal/sessions",
        json=body,
        headers={"Authorization": f"Bearer {service_token('rounds')}"},
    )

    assert response.status_code == 201
    assert created["question_seconds"] == 45


def test_a_question_past_its_time_counts_as_wrong(monkeypatch):
    expired = timed(shown_seconds_ago=40)
    saved = []

    async def fake_get(session_id):
        return expired

    async def fake_add(answer):
        saved.append(answer)
        expired.answers = [answer]

        return True

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "add_answer", fake_add)

    asyncio.run(get_owned_session(expired.id, CANDIDATE))

    assert [(a.question_id, a.option_index, a.correct, a.score) for a in saved] == [
        (QUESTION_ID, None, False, 0)
    ]


def test_a_question_within_its_time_is_left_alone(monkeypatch):
    running = timed(shown_seconds_ago=10)

    async def fake_get(session_id):
        return running

    async def never(answer):
        raise AssertionError("must not time out a running question")

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "add_answer", never)

    assert asyncio.run(get_owned_session(running.id, CANDIDATE)).answers == []


def test_no_answer_once_the_question_timed_out():
    timed_out = Answer(question_id=QUESTION_ID, option_index=None, correct=False, score=0)
    row = timed(shown_seconds_ago=40, answers=[timed_out])

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            submit_session_answer(row, AnswerCreate(question_id=QUESTION_ID, option_index=0))
        )

    assert error.value.status_code == 409
    assert error.value.detail == TIME_UP


def test_only_the_question_on_screen_can_be_answered():
    row = timed(shown_seconds_ago=5)
    row.question_shown_at = None

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            submit_session_answer(row, AnswerCreate(question_id=QUESTION_ID, option_index=0))
        )

    assert error.value.status_code == 409
