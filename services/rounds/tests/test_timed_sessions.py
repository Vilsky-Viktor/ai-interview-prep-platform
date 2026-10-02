import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from prepza_common.user import User

from app.constants.rounds import TIME_UP
from app.models.sessions import Session
from app.schemas.rounds import AnswerCreate
from app.service_auth import service_token
from app.services.session_access import get_owned_session
from app.services.session_answers import submit_session_answer
from app.storage import sessions

CANDIDATE = User(uid="cand", email="cand@example.com", email_verified=True)
INVITE_ID = uuid4()


def timed(deadline, status="in_progress"):
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=INVITE_ID,
        topic_title="Python",
        share_results=False,
        status=status,
        questions=[{"id": "q1", "text": "Q?", "options": []}],
        final_score=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        deadline=deadline,
        answers=[],
    )


def test_starting_a_timed_interview_sets_one_deadline(client, monkeypatch):
    created = {}

    async def no_sessions(invite_id):
        return []

    async def fake_create(user_id, invite_id, share_results, topics, deadline):
        created["deadline"] = deadline

        return []

    monkeypatch.setattr(sessions, "list_for_invite", no_sessions)
    monkeypatch.setattr(sessions, "create_many", fake_create)
    body = {
        "user_id": "cand",
        "candidate_invite_id": str(INVITE_ID),
        "share_results": False,
        "topics": [],
        "time_limit_minutes": 45,
    }

    response = client.post(
        "/internal/sessions", json=body, headers={"Authorization": f"Bearer {service_token()}"}
    )

    left = created["deadline"] - datetime.now(UTC)
    assert response.status_code == 201
    assert timedelta(minutes=44) < left <= timedelta(minutes=45)


def test_an_expired_section_finishes_the_whole_interview(monkeypatch):
    expired = timed(datetime.now(UTC) - timedelta(seconds=1))
    finished = timed(expired.deadline, status="finished")
    calls = []

    async def fake_get(session_id):
        return finished if calls else expired

    async def fake_finish_expired(invite_ids):
        calls.append(invite_ids)

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "finish_expired", fake_finish_expired)

    row = asyncio.run(get_owned_session(expired.id, CANDIDATE))

    assert calls == [[INVITE_ID]]
    assert row.status == "finished"


def test_a_running_section_is_left_alone(monkeypatch):
    running = timed(datetime.now(UTC) + timedelta(minutes=5))

    async def fake_get(session_id):
        return running

    async def never(invite_ids):
        raise AssertionError("must not finish a running interview")

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(sessions, "finish_expired", never)

    assert asyncio.run(get_owned_session(running.id, CANDIDATE)).status == "in_progress"


def test_no_answers_once_time_is_up():
    row = timed(datetime.now(UTC) - timedelta(minutes=1), status="finished")

    with pytest.raises(HTTPException) as error:
        asyncio.run(submit_session_answer(row, AnswerCreate(question_id=uuid4(), option_index=0)))

    assert error.value.status_code == 409
    assert error.value.detail == TIME_UP
