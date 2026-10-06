import asyncio
import uuid
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.integrations import library, rounds
from app.services import candidate_start
from app.storage import invites

INVITE = SimpleNamespace(id=uuid.uuid4(), extra_time=0)
INTERVIEW = SimpleNamespace(set_id=uuid.uuid4(), question_seconds=60, topic_limits={})


@pytest.fixture
def steps(monkeypatch):
    """What happened, in order, as a candidate starts."""
    done = []

    async def same(interview):
        return interview

    async def content(set_id):
        return {"id": str(set_id), "topics": [{"id": "t", "title": "Python", "questions": []}]}

    async def create(payload):
        done.append("sessions")

        return [{"id": str(uuid.uuid4()), "topic_title": "Python", "status": "in_progress"}]

    async def start(invite_id, user_id):
        done.append("started")

        return True

    async def erase(invite_ids):
        done.append("erased")

    monkeypatch.setattr(candidate_start, "attach_set", same)
    monkeypatch.setattr(library, "get_content", content)
    monkeypatch.setattr(rounds, "create_sessions", create)
    monkeypatch.setattr(rounds, "delete_invite_sessions", erase)
    monkeypatch.setattr(invites, "start", start)

    return done


def test_the_invite_is_marked_started_once_its_sessions_exist(steps):
    out = asyncio.run(candidate_start.start_sessions(INVITE, INTERVIEW, "cand"))

    assert [row.topic_title for row in out.sessions] == ["Python"]
    assert steps == ["sessions", "started"]


def test_rounds_failing_leaves_the_invite_unstarted_so_expiry_frees_its_credits(steps, monkeypatch):
    async def down(payload):
        raise httpx.ConnectError("rounds is down")

    monkeypatch.setattr(rounds, "create_sessions", down)

    with pytest.raises(httpx.ConnectError):
        asyncio.run(candidate_start.start_sessions(INVITE, INTERVIEW, "cand"))

    assert steps == []


def test_an_invite_revoked_while_starting_loses_its_sessions(steps, monkeypatch):
    async def gone(invite_id, user_id):
        return False

    monkeypatch.setattr(invites, "start", gone)

    with pytest.raises(HTTPException) as refused:
        asyncio.run(candidate_start.start_sessions(INVITE, INTERVIEW, "cand"))

    assert refused.value.status_code == 404
    assert steps == ["sessions", "erased"]
