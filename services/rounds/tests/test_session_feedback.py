from datetime import UTC, datetime
from uuid import uuid4

import httpx

from app.auth import current_user
from app.integrations import feedback
from app.main import app
from app.models.sessions import Session
from app.schemas.user import User
from app.storage import sessions

QUESTION_ID = uuid4()


def owned_session():
    return Session(
        id=uuid4(),
        user_id="cand",
        topic_id=uuid4(),
        interview_set_id=uuid4(),
        candidate_invite_id=uuid4(),
        topic_title="Python",
        mode="open",
        share_results=False,
        status="in_progress",
        questions=[{"id": str(QUESTION_ID), "text": "What is the GIL?"}],
        started_at=datetime.now(UTC),
        answers=[],
    )


def test_candidate_rates_only_own_session_questions(client, monkeypatch):
    row = owned_session()
    calls = []

    async def fake_get(_session_id):
        return row

    async def fake_rate(question_id, user_id, value):
        calls.append((question_id, user_id, value))
        status = 204 if len(calls) == 1 else 409

        return httpx.Response(
            status,
            json=None if status == 204 else {"detail": "Already rated"},
            request=httpx.Request("PUT", "http://library"),
        )

    monkeypatch.setattr(sessions, "get", fake_get)
    monkeypatch.setattr(feedback, "rate", fake_rate)
    app.dependency_overrides[current_user] = lambda: User(
        uid="cand", email="cand@example.com", email_verified=True
    )
    base = f"/sessions/{row.id}/questions"

    assert client.put(f"{base}/{uuid4()}/rating", json={"value": 1}).status_code == 404
    assert client.put(f"{base}/{QUESTION_ID}/rating", json={"value": 1}).status_code == 204
    assert client.put(f"{base}/{QUESTION_ID}/rating", json={"value": -1}).status_code == 409
    assert calls[0] == (QUESTION_ID, "cand", 1)

    app.dependency_overrides.clear()
