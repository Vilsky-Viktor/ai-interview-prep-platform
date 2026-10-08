import asyncio
import uuid

import httpx
import pytest
from fastapi import HTTPException
from prepza_common.user import User

from app.auth import user_with_token
from app.constants.limits import MAX_AUDIO_SECONDS, MESSAGES_PER_USER_HOUR
from app.integrations import services
from app.main import app
from app.models.conversations import Conversation
from app.services import conversations as conversation_service
from app.services import events, turns
from app.storage import conversations

COMPANY = uuid.UUID("8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f")
ANN = User(uid="ann", email="ann@example.com", email_verified=True)


@pytest.fixture
def signed_in():
    app.dependency_overrides[user_with_token] = lambda: (ANN, "user-token")

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def created(monkeypatch):
    """Conversations created; none must be when a message is refused."""
    made = []

    async def create(user_id, company_id, title):
        made.append((user_id, company_id, title))

    monkeypatch.setattr(conversations, "create", create)

    return made


def companies_answers(monkeypatch, status):
    async def get(service, path, query, token, language):
        return httpx.Response(status, json={}, request=httpx.Request("GET", "http://companies"))

    monkeypatch.setattr(services, "get", get)


def test_a_message_too_long_is_refused_in_the_users_language(client, signed_in):
    response = client.post(
        "/chat", json={"message": "x" * 2_001}, headers={"Accept-Language": "de"}
    )

    assert response.status_code == 422
    assert "Die Frage ist zu lang." in response.text


def test_paused_or_over_a_limit_is_refused_before_anything_is_saved(
    client, signed_in, created, monkeypatch
):
    async def paused(redis):
        raise HTTPException(503, "paused")

    monkeypatch.setattr(turns, "refuse_if_paused", paused)
    assert client.post("/chat", json={"message": "Hi"}).status_code == 503

    async def over(redis, user_id, company_id):
        raise HTTPException(429, "over")

    async def not_paused(redis):
        pass

    monkeypatch.setattr(turns, "refuse_if_paused", not_paused)
    monkeypatch.setattr(turns.limits, "check", over)
    assert client.post("/chat", json={"message": "Hi"}).status_code == 429
    assert created == []


def test_a_new_conversation_only_about_a_company_the_user_can_see(
    client, signed_in, created, monkeypatch
):
    async def not_paused(redis):
        pass

    monkeypatch.setattr(turns, "refuse_if_paused", not_paused)
    companies_answers(monkeypatch, 404)
    response = client.post("/chat", json={"message": "Hi", "company_id": str(COMPANY)})

    assert (response.status_code, response.json()["detail"]) == (404, "Company not found")
    assert created == []


def test_the_panel_reads_its_limits(client, signed_in):
    config = client.get("/config").json()

    assert config["max_message_length"] == 2_000
    assert config["max_audio_seconds"] == MAX_AUDIO_SECONDS
    assert config["messages_per_hour"] == MESSAGES_PER_USER_HOUR


def test_signed_out_and_unsigned_calls_are_refused(client):
    assert client.post("/chat", json={"message": "Hi"}).status_code in (401, 403)
    assert client.get("/conversations").status_code in (401, 403)
    response = client.request("DELETE", "/internal/users/ann", json={"email": "a@b.c"})
    assert response.status_code in (401, 403)
    forged = {"Authorization": "Bearer forged"}
    response = client.post("/internal/users/ann/export", json={"email": "a@b.c"}, headers=forged)
    assert response.status_code == 401


@pytest.mark.parametrize("status, kept", [(200, True), (403, False), (404, False)])
def test_a_conversation_about_a_company_lost_to_the_user_is_deleted_on_opening(
    monkeypatch, status, kept
):
    conversation = Conversation(id=uuid.uuid4(), user_id="ann", company_id=COMPANY, title="t")
    deleted = []

    async def owned(conversation_id, user_id):
        return conversation

    async def delete_one(conversation_id):
        deleted.append(conversation_id)

    monkeypatch.setattr(conversations, "owned", owned)
    monkeypatch.setattr(conversations, "delete_one", delete_one)
    companies_answers(monkeypatch, status)
    opening = conversation_service.open_conversation(conversation.id, "ann", "token", "en")

    if kept:
        assert asyncio.run(opening) is conversation
        assert deleted == []
    else:
        with pytest.raises(HTTPException) as error:
            asyncio.run(opening)

        assert error.value.status_code == 404
        assert deleted == [conversation.id]


def test_companies_failing_is_a_503_not_a_deletion(monkeypatch):
    companies_answers(monkeypatch, 502)

    with pytest.raises(HTTPException) as error:
        asyncio.run(conversation_service.has_access(COMPANY, "token", "en"))

    assert error.value.status_code == 503


def test_only_company_deleted_is_handled_and_a_malformed_one_is_dropped(monkeypatch):
    deleted = []

    async def delete_company(company_id):
        deleted.append(company_id)

        return 0

    monkeypatch.setattr(events.conversations, "delete_company", delete_company)
    asyncio.run(events.handle("interview.deleted", {"interview_id": str(COMPANY)}))
    asyncio.run(events.handle("company.deleted", {"company_id": "not-a-uuid"}))
    asyncio.run(events.handle("company.deleted", {"company_id": str(COMPANY)}))

    assert deleted == [COMPANY]


def test_a_visitors_earlier_chat_is_cut_to_a_messages_length_and_limited_in_count(
    client, signed_in
):
    from app.schemas.chat import ChatRequest

    body = ChatRequest(message="Hi", earlier=[{"role": "assistant", "content": "x" * 3_000}])
    assert len(body.earlier[0].content) == 2_000

    too_many = [{"role": "user", "content": "Hi"}] * 21
    response = client.post("/chat", json={"message": "Hi", "earlier": too_many})
    assert response.status_code == 422
