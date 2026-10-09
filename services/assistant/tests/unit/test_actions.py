import asyncio
import json
import uuid

import httpx
import pytest
from fastapi import HTTPException
from prepza_common.user import User

from app.constants.actions_flow import ACTION_TTL_SECONDS
from app.integrations import services
from app.models.answers import Turn
from app.services import actions, chat
from app.services.registry import tools
from app.storage import actions as store

ANN = User(uid="ann", email="ann@example.com", email_verified=True, name="Ann Lee")
BOB = User(uid="bob", email="bob@example.com", email_verified=True)
CONVERSATION = uuid.uuid4()
COMPANY = "8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f"
TURN = Turn(CONVERSATION, "ann", None, "token", "en", frozenset({COMPANY}), "Ann Lee")


class Writes(list):
    """The services' writes; each answers `status`."""

    status = 201


class Pipeline:
    """Runs its commands one by one on the fake."""

    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def set(self, *args, **kwargs):
        self.commands.append(self.redis.set(*args, **kwargs))

    def sadd(self, *args):
        pass

    def expire(self, *args):
        pass

    async def execute(self):
        for command in self.commands:
            await command


class FakeRedis:
    """Redis's strings with their expiry, as the actions use them."""

    def __init__(self):
        self.values = {}
        self.expiry = {}

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.values:
            return None

        self.values[key] = value
        self.expiry[key] = ex

        return True

    async def get(self, key):
        return self.values.get(key)

    def pipeline(self, transaction=True):
        return Pipeline(self)

    async def getdel(self, key):
        self.expiry.pop(key, None)

        return self.values.pop(key, None)


@pytest.fixture
def redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(store, "get_redis", lambda: fake)
    monkeypatch.setattr(actions, "get_redis", lambda: fake)

    async def nothing(*args, **kwargs):
        pass

    async def owned(conversation_id, user_id, token, language):
        return None

    async def companies(token, language):
        return frozenset({COMPANY})

    monkeypatch.setattr(actions, "refuse_if_paused", nothing)
    monkeypatch.setattr(actions, "hit", nothing)
    monkeypatch.setattr(actions.limits, "check", nothing)
    monkeypatch.setattr(actions, "open_conversation", owned)
    monkeypatch.setattr(actions, "user_companies", companies)

    return fake


@pytest.fixture
def writes(monkeypatch):
    """The services' writes, answering 201 with a new company."""
    made = Writes()

    async def send(service, method, path, query, body, token, language, idempotency_key=None):
        made.append((service, method, path, body, token, idempotency_key))
        request = httpx.Request(method, f"http://{service}{path}")

        return httpx.Response(
            made.status,
            json={"id": COMPANY, "name": body["name"], "role": "owner"},
            request=request,
        )

    monkeypatch.setattr(services, "send", send)

    return made


def prepared(redis) -> uuid.UUID:
    result = asyncio.run(actions.prepare(tools()["create_company"], {"name": "Acme"}, TURN))

    return uuid.UUID(result.block["action_id"])


def test_preparing_runs_nothing_and_keeps_the_action_in_redis_for_ten_minutes(redis, writes):
    action_id = prepared(redis)
    kept = json.loads(redis.values[store.key(action_id)])

    assert writes == []
    assert {key: kept[key] for key in ("user_id", "conversation_id", "company_id", "tool")} == {
        "user_id": "ann",
        "conversation_id": str(CONVERSATION),
        "company_id": None,
        "tool": "create_company",
    }
    assert kept["arguments"] == {"name": "Acme"}
    assert kept["card"]["preview"] == {"name": "Acme"}
    assert redis.expiry[store.key(action_id)] == ACTION_TTL_SECONDS == 600


def test_a_card_shows_exactly_what_runs():
    block = actions.card(uuid.uuid4(), tools()["create_company"], {"name": "Acme"}, "pending")

    assert (block["kind"], block["tool"], block["preview"]) == (
        "confirm",
        "create_company",
        {"name": "Acme"},
    )
    assert block["destructive"] is False


def test_a_confirmed_action_runs_once_as_the_user_and_a_second_confirm_finds_it_gone(redis, writes):
    action_id = prepared(redis)
    *_, block = asyncio.run(actions.run(CONVERSATION, action_id, ANN, "fresh", "en"))

    assert writes == [
        ("companies", "POST", "/companies", {"name": "Acme"}, "fresh", str(action_id))
    ]
    assert (block["state"], block["links"]) == ("done", [f"/companies/{COMPANY}/interviews"])
    assert store.key(action_id) not in redis.values

    with pytest.raises(HTTPException) as again:
        asyncio.run(actions.run(CONVERSATION, action_id, ANN, "fresh", "en"))

    assert again.value.status_code == 409
    assert len(writes) == 1


def test_two_confirms_at_once_run_it_once(redis, writes):
    action_id = prepared(redis)

    async def both():
        return await asyncio.gather(
            actions.run(CONVERSATION, action_id, ANN, "t", "en"),
            actions.run(CONVERSATION, action_id, ANN, "t", "en"),
            return_exceptions=True,
        )

    outcomes = asyncio.run(both())

    assert len(writes) == 1
    assert sum(isinstance(outcome, HTTPException) for outcome in outcomes) == 1


@pytest.mark.parametrize("user, conversation", [(BOB, CONVERSATION), (ANN, uuid.uuid4())])
def test_only_its_user_in_its_conversation_may_confirm_it(redis, writes, user, conversation):
    action_id = prepared(redis)

    with pytest.raises(HTTPException) as refused:
        asyncio.run(actions.run(conversation, action_id, user, "t", "en"))

    assert refused.value.status_code == 404
    assert writes == []
    # Still there for its own user.
    assert store.key(action_id) in redis.values


def test_a_company_no_longer_the_users_is_refused_on_confirm(redis, writes, monkeypatch):
    async def get(service, path, query, token, language):
        return httpx.Response(200, json={"name": "Acme"}, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    arguments = {"company_id": COMPANY, "title": "Acme 2"}
    result = asyncio.run(actions.prepare(tools()["rename_company"], arguments, TURN))
    assert result.block["subject"] == "Acme"

    async def none_left(token, language):
        return frozenset()

    monkeypatch.setattr(actions, "user_companies", none_left)

    with pytest.raises(HTTPException) as refused:
        asyncio.run(actions.run(CONVERSATION, result.action_id, ANN, "t", "en"))

    assert refused.value.status_code == 404
    assert writes == []


def test_an_expired_or_cancelled_action_is_gone(redis, writes):
    action_id = prepared(redis)
    asyncio.run(actions.cancel(CONVERSATION, action_id, ANN, "t", "en"))

    with pytest.raises(HTTPException):
        asyncio.run(actions.run(CONVERSATION, action_id, ANN, "t", "en"))

    expired = prepared(redis)
    # Redis drops it after ACTION_TTL_SECONDS.
    redis.values.pop(store.key(expired))

    with pytest.raises(HTTPException) as gone:
        asyncio.run(actions.run(CONVERSATION, expired, ANN, "t", "en"))

    assert gone.value.status_code == 409
    assert writes == []


def test_a_refused_token_runs_nothing_and_keeps_the_action_for_a_fresh_one(redis, writes):
    action_id = prepared(redis)
    writes.status = 401

    with pytest.raises(HTTPException) as refused:
        asyncio.run(actions.run(CONVERSATION, action_id, ANN, "stale", "en"))

    assert refused.value.status_code == 401
    assert store.key(action_id) in redis.values


def test_a_tool_naming_another_company_is_refused_before_anything_is_called(monkeypatch):
    called = []

    async def call_tools(calls, token, language, company_id):
        called.extend(calls)

        return []

    monkeypatch.setattr(chat, "call_tools", call_tools)
    other = {"company_id": "00000000-0000-0000-0000-000000000000"}
    [result] = asyncio.run(chat.step_results([("get_company", other)], TURN))

    assert called == []
    assert result.content["error"] == 404


def test_signing_out_tells_the_panel_to_and_calls_nothing(monkeypatch):
    called = []

    async def call_tools(calls, token, language, company_id):
        called.extend(calls)

        return []

    monkeypatch.setattr(chat, "call_tools", call_tools)
    [result] = asyncio.run(chat.step_results([("sign_out", {})], TURN))
    assert called == []
    assert result.block is None

    emitted = []
    answer = chat.Answer()
    call = {"name": "sign_out", "args": {}, "id": "c1", "type": "tool_call"}
    asyncio.run(chat.run_tools([call], TURN, answer, emitted.append))

    assert {"sign_out": True} in emitted
    assert answer.blocks == []


def test_an_action_about_something_the_user_cant_see_gets_no_card(redis, writes, monkeypatch):
    async def get(service, path, query, token, language):
        return httpx.Response(404, json={}, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    interview = "11111111-1111-4111-8111-111111111111"
    result = asyncio.run(
        actions.prepare(tools()["delete_interview"], {"interview_id": interview}, TURN)
    )

    assert result.block is None
    assert result.content["error"] == 404
    assert redis.values == {}


def test_a_list_subject_is_the_matching_item(monkeypatch):
    members = [{"id": "m1", "email": "bo@example.com"}, {"id": "m2", "email": "cy@example.com"}]

    async def get(service, path, query, token, language):
        assert (path, query) == ("/members", {"company_id": COMPANY})

        return httpx.Response(200, json=members, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    arguments = {"member_id": "m2", "company_id": COMPANY}

    found = asyncio.run(actions.subject_of(tools()["remove_member"], arguments, "t", "en"))

    assert found == members[1]


def test_a_done_card_names_what_the_action_made(redis, writes):
    action_id = prepared(redis)
    *_, block = asyncio.run(actions.run(CONVERSATION, action_id, ANN, "t", "en"))

    assert block["result_label"] == "Acme"


def test_a_change_sends_only_what_differs_from_now(redis, monkeypatch):
    interview = {
        "id": "i1",
        "title": "Backend",
        "pass_mark": 60,
        "question_seconds": 10,
        "hired": False,
    }

    async def get(service, path, query, token, language):
        return httpx.Response(200, json=interview, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    tool = tools()["set_pass_mark"]
    arguments = {"interview_id": "11111111-1111-4111-8111-111111111111", "pass_mark": 75}
    result = asyncio.run(actions.prepare(tool, arguments, TURN))

    assert result.block["preview"] == {"pass_mark": 75}
    assert result.block["subject"] == "Backend"

    same = {"interview_id": arguments["interview_id"], "pass_mark": 60}
    nothing = asyncio.run(actions.prepare(tools()["set_pass_mark"], same, TURN))
    assert nothing.block is None
    assert nothing.content["error"] == 422


def test_each_setting_is_its_own_action_and_needs_its_value():
    for name, field in [
        ("set_pass_mark", "pass_mark"),
        ("set_question_seconds", "question_seconds"),
        ("mark_hired", "hired"),
    ]:
        parameters = tools()[name].parameters

        assert set(parameters["properties"]) == {"interview_id", field}
        assert set(parameters["required"]) == {"interview_id", field}


def test_deleting_a_company_says_how_many_of_its_credits_are_lost(redis, monkeypatch):
    async def get(service, path, query, token, language):
        body = (
            {"available": 900, "low": False, "candidates": 3}
            if path.endswith("/credits")
            else {"name": "Acme"}
        )

        return httpx.Response(200, json=body, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    result = asyncio.run(actions.prepare(tools()["delete_company"], {"company_id": COMPANY}, TURN))

    assert result.block["credits"] == {"available": 900, "candidates": 3}
    assert result.block["destructive"] is True


def test_a_company_without_credits_loses_none(redis, monkeypatch):
    async def get(service, path, query, token, language):
        body = (
            {"available": 0, "low": True, "candidates": 0}
            if path.endswith("/credits")
            else {"name": "A"}
        )

        return httpx.Response(200, json=body, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", get)
    result = asyncio.run(actions.prepare(tools()["delete_company"], {"company_id": COMPANY}, TURN))

    assert result.block["credits"] is None
