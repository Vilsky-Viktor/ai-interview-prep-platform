"""Retention, company.deleted and the limits against the real database and Redis."""

import base64
import json
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import update

from app.constants.limits import MESSAGES_PER_USER_HOUR, TOKENS_PER_USER_DAY
from app.integrations.redis import get_redis
from app.main import app
from app.models.conversations import Conversation
from app.routers import schedules
from app.schemas.chat import EarlierTurn
from app.services import limits
from app.storage import conversations, messages
from app.storage.db import Session


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://assistant")


async def idle_since(conversation_id, days: int) -> None:
    async with Session() as session:
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.now(UTC) - timedelta(days=days))
        )
        await session.commit()


def test_retention_deletes_idle_conversations_in_batches_and_is_safe_to_repeat(run, monkeypatch):
    monkeypatch.setattr(schedules, "RETENTION_BATCH", 2)
    user = f"retention-{uuid.uuid4().hex[:8]}"

    async def scenario():
        old = [await conversations.create(user, None, f"old {i}") for i in range(5)]
        recent = await conversations.create(user, None, "recent")

        for conversation in old:
            await idle_since(conversation.id, 91)

        await idle_since(recent.id, 89)

        async with client() as api:
            first = await api.post("/internal/schedules/retention")
            again = await api.post("/internal/schedules/retention")

        left = await conversations.of_user(user, None, 0, 100)

        return first, again, left

    first, again, left = run(scenario())

    assert (first.status_code, again.status_code) == (204, 204)
    assert [item.title for item in left] == ["recent"]


def push(event_type: str, data: dict) -> dict:
    return {
        "message": {
            "data": base64.b64encode(json.dumps(data).encode()).decode(),
            "attributes": {"type": event_type},
            "messageId": uuid.uuid4().hex,
        },
        "subscription": "assistant-events",
    }


def test_company_deleted_deletes_its_conversations_once_and_again_changes_nothing(run):
    gone, other = uuid.uuid4(), uuid.uuid4()
    user = f"members-{uuid.uuid4().hex[:8]}"

    async def scenario():
        await conversations.create(user, gone, "About the gone company")
        await conversations.create(user, other, "About another")
        await conversations.create(user, None, "About none")
        event = push("company.deleted", {"company_id": str(gone)})

        async with client() as api:
            answers = [(await api.post("/internal/events", json=event)).status_code for _ in "12"]

        return answers, await conversations.of_user(user, None, 0, 100)

    answers, left = run(scenario())

    assert answers == [204, 204]
    assert sorted(item.title for item in left) == ["About another", "About none"]


def test_the_limits_count_in_redis(run):
    user = f"limits-{uuid.uuid4().hex[:8]}"

    async def scenario():
        redis = get_redis()

        for _ in range(MESSAGES_PER_USER_HOUR):
            await limits.check(redis, user, None)

        with pytest.raises(HTTPException) as over_messages:
            await limits.check(redis, user, None)

        spender = f"{user}-spender"
        await limits.check(redis, spender, None)
        await limits.record(redis, spender, None, TOKENS_PER_USER_DAY + 1)

        with pytest.raises(HTTPException) as over_budget:
            await limits.check(redis, spender, None)

        # Everyone's totals, so repeated runs don't fill them.
        await redis.delete("spend:assistant:all", "rate:assistant:all")

        return over_messages.value.status_code, over_budget.value.status_code

    assert run(scenario()) == (429, 429)


def test_a_visitors_chat_starts_the_new_conversation_in_its_order(run):
    user = f"earlier-{uuid.uuid4().hex[:8]}"
    turns = [
        EarlierTurn(role="user", content="What is prepza?"),
        EarlierTurn(role="assistant", content="A hiring test."),
        EarlierTurn(role="user", content="How much?"),
        EarlierTurn(role="assistant", content="$1–3 a candidate."),
    ]

    async def scenario():
        conversation = await conversations.create(user, None, "Sign in")
        await messages.add_earlier(conversation.id, turns)
        await messages.add_question(conversation.id, "Create a company", "text")

        return await messages.recent(conversation.id, 20)

    found = run(scenario())

    assert [(message.role, message.content) for message in found] == [
        *[(turn.role, turn.content) for turn in turns],
        ("user", "Create a company"),
    ]
