"""A conversation through the routes: a real database and Redis, companies answering as a
throwaway Auth emulator user, and a scripted model instead of OpenAI."""

import json
import os
import uuid

import httpx
from langchain_core.messages import ToolMessage
from prepza_common.service_auth import issue_token

from app.integrations import llm
from app.main import app
from app.storage import conversations, messages
from tests.fake_model import FakeModel, calls, text


def events(body: str) -> list[dict]:
    return [json.loads(line[5:]) for line in body.splitlines() if line.startswith("data:")]


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://assistant")


def library() -> dict:
    """Library's signed token, as it calls to delete or export a user's data."""
    token = issue_token("library", "assistant", os.environ["SERVICE_SECRET"])

    return {"Authorization": f"Bearer {token}"}


def test_a_conversation_is_streamed_saved_listed_exported_and_deleted(run, user, monkeypatch):
    uid, token = user
    model = FakeModel(
        calls(("list_companies", {})), text("You have no companies yet."), text("Still none.")
    )
    monkeypatch.setattr(llm, "get_chat_model", lambda: model)
    headers = {"Authorization": f"Bearer {token}", "Accept-Language": "en"}

    async def scenario():
        async with client() as api:
            first = await api.post("/chat", json={"message": "My companies?"}, headers=headers)
            first = events(first.text)
            conversation_id = first[0]["conversation"]["id"]
            body = {"conversation_id": conversation_id, "message": "And now?", "page": "/companies"}
            second = events((await api.post("/chat", json=body, headers=headers)).text)
            listed = (await api.get("/conversations", headers=headers)).json()
            opened = (await api.get(f"/conversations/{conversation_id}", headers=headers)).json()
            stored = await messages.recent(uuid.UUID(conversation_id), 20)
            body = {"email": "ann@example.com"}
            exported = await api.post(f"/internal/users/{uid}/export", json=body, headers=library())
            deleted = await api.request(
                "DELETE", f"/internal/users/{uid}", json=body, headers=library()
            )
            after = (await api.get("/conversations", headers=headers)).json()

            return first, second, listed, opened, stored, exported.json(), deleted, after

    first, second, listed, opened, stored, exported, deleted, after = run(scenario())

    assert [list(event) for event in first] == [
        ["conversation"],
        ["tool"],
        ["tool"],
        ["block"],
        *[["delta"]] * 5,
        ["done"],
    ]
    assert first[2]["tool"]["state"] == "done"
    assert second[-1]["done"]["message_id"] == opened["messages"][-1]["id"]
    # The second turn's model reads the first one's tool result again.
    earlier = [m for m in model.prompts[2] if isinstance(m, ToolMessage)]
    assert json.loads(earlier[0].content) == {"data": [], "source": "list_companies"}
    assert [item["title"] for item in listed] == ["My companies?"]
    assert [(m["role"], m["content"], m["status"]) for m in opened["messages"]] == [
        ("user", "My companies?", "complete"),
        ("assistant", "You have no companies yet.", "complete"),
        ("user", "And now?", "complete"),
        ("assistant", "Still none.", "complete"),
    ]
    answer, [call] = stored[1]
    assert (answer.input_tokens, answer.output_tokens) == (20, 10)
    assert (call.tool, call.status_code, call.state, call.result["data"]) == (
        "list_companies",
        200,
        "done",
        [],
    )
    [conversation] = exported["assistant_conversations"]
    assert len(conversation["messages"]) == 4
    # Never what the tools read.
    assert "result" not in json.dumps(exported) and "blocks" not in json.dumps(exported)
    assert deleted.status_code == 204
    assert after == []


def test_a_company_the_user_cant_see_is_refused_and_a_stored_one_is_deleted(run, user):
    uid, token = user
    headers = {"Authorization": f"Bearer {token}"}
    company_id = uuid.uuid4()

    async def scenario():
        # Stored while the user could see it; they've since lost access.
        stored = await conversations.create(uid, company_id, "Old")

        async with client() as api:
            body = {"message": "Hi", "company_id": str(company_id)}
            started = await api.post("/chat", json=body, headers=headers)
            opened = await api.get(f"/conversations/{stored.id}", headers=headers)

        return started, opened, await conversations.owned(stored.id, uid)

    started, opened, left = run(scenario())

    assert (started.status_code, started.json()["detail"]) == (404, "Company not found")
    assert opened.status_code == 404
    assert left is None


def test_someone_elses_conversation_is_not_found(run, user):
    _, token = user
    headers = {"Authorization": f"Bearer {token}"}

    async def scenario():
        other = await conversations.create("someone-else", None, "Theirs")

        async with client() as api:
            opened = await api.get(f"/conversations/{other.id}", headers=headers)
            deleted = await api.delete(f"/conversations/{other.id}", headers=headers)

        return opened, deleted, await conversations.owned(other.id, "someone-else")

    opened, deleted, kept = run(scenario())

    assert (opened.status_code, deleted.status_code) == (404, 404)
    assert kept is not None
