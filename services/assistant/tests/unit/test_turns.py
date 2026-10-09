import asyncio
import json
import uuid

import anyio
import httpx
import pytest
from prepza_common.sse import KEEP_ALIVE

from app.constants.chat import CHAT_FAILED, Status
from app.integrations import llm, services
from app.models.answers import Turn
from app.services import turns
from tests.fake_model import FakeModel, calls, text

TURN = Turn(uuid.uuid4(), "ann", None, "user-token", "en")
MESSAGE_ID = uuid.uuid4()


class Saved(list):
    """The answers saved, as (status, content, tools), and the tokens recorded."""

    tokens: list


@pytest.fixture
def saved(monkeypatch):
    found = Saved()
    found.tokens = []

    async def add_answer(conversation_id, answer, status):
        found.append((status, answer.content, [result.tool for result in answer.results]))

        return MESSAGE_ID

    async def record(redis, user_id, company_id, tokens):
        found.tokens.append((user_id, tokens))

    async def get(service, path, query, token, language):
        return httpx.Response(
            200, json={"email": "ann@example.com"}, request=httpx.Request("GET", "http://x")
        )

    async def no_title(turn):
        return None

    monkeypatch.setattr(turns.messages, "add_answer", add_answer)
    monkeypatch.setattr(turns.titles, "refresh", no_title)
    monkeypatch.setattr(turns.limits, "record", record)
    monkeypatch.setattr(services, "get", get)

    return found


def script(monkeypatch, *replies) -> FakeModel:
    fake = FakeModel(*replies)
    monkeypatch.setattr(llm, "get_chat_model", lambda: fake)

    return fake


def events_of(chunks: list[str]) -> list:
    return [json.loads(chunk.removeprefix("data: ")) for chunk in chunks if chunk != KEEP_ALIVE]


def collect() -> list[str]:
    async def read():
        return [chunk async for chunk in turns.stream(TURN, [])]

    return asyncio.run(read())


def test_a_turns_events_come_in_order_and_end_with_the_saved_message(monkeypatch, saved):
    script(monkeypatch, calls(("get_me", {})), text("You're Ann."))

    assert events_of(collect()) == [
        {"conversation": {"id": str(TURN.conversation_id)}},
        {"tool": {"name": "get_me", "state": "running", "label": "Reading your account…"}},
        {"tool": {"name": "get_me", "state": "done", "label": "Reading your account…"}},
        {"delta": "You're"},
        {"delta": " Ann."},
        {"done": {"message_id": str(MESSAGE_ID)}},
    ]
    assert saved == [(Status.COMPLETE, "You're Ann.", ["get_me"])]
    assert saved.tokens == [("ann", 30)]


def test_a_quiet_stream_sends_keep_alives(monkeypatch, saved):
    monkeypatch.setattr(turns, "KEEP_ALIVE_SECONDS", 0.01)
    script(monkeypatch, text("Thinking slowly", sleep=0.1))

    chunks = collect()

    assert KEEP_ALIVE in chunks
    assert events_of(chunks)[-1] == {"done": {"message_id": str(MESSAGE_ID)}}


def test_a_turn_out_of_time_fails_and_keeps_its_text(monkeypatch, saved):
    monkeypatch.setattr(turns, "TURN_SECONDS", 0.05)
    script(monkeypatch, text("Partly done", sleep=5))

    events = events_of(collect())

    assert events[-1] == {"error": CHAT_FAILED}
    assert saved == [(Status.FAILED, "Partly", [])]


def test_a_failing_model_is_an_error_to_try_again(monkeypatch, saved):
    script(monkeypatch, RuntimeError("OpenAI is down"))

    assert events_of(collect())[-1] == {"error": CHAT_FAILED}
    assert saved == [(Status.FAILED, "", [])]


def test_an_expired_session_says_so_with_its_code(monkeypatch, saved):
    async def refused(service, path, query, token, language):
        return httpx.Response(401, json={}, request=httpx.Request("GET", "http://x"))

    monkeypatch.setattr(services, "get", refused)
    script(monkeypatch, calls(("get_pause", {})))

    last = events_of(collect())[-1]

    assert last["code"] == "session_expired"
    assert saved[0][0] == Status.FAILED


def test_an_answer_that_cant_be_saved_is_an_error(monkeypatch, saved):
    async def gone(conversation_id, answer, status):
        raise RuntimeError("conversation deleted")

    monkeypatch.setattr(turns.messages, "add_answer", gone)
    script(monkeypatch, text("Hi"))

    assert events_of(collect())[-1] == {"error": CHAT_FAILED}


@pytest.mark.parametrize("how", ["cancel", "scope", "close"])
def test_a_stopped_turn_is_saved_cancelled_with_its_text_so_far(monkeypatch, saved, how):
    """The server cancels the request when the client goes (Starlette cancels its task group's
    scope, which cancels every await in it again), or closes the stream: the turn stops and
    saves what it had before the request ends."""
    script(monkeypatch, text("Half an answer", sleep=5))

    async def scenario():
        stream = turns.stream(TURN, [])

        if how == "close":
            async for chunk in stream:
                if "delta" in chunk:
                    break

            await stream.aclose()

            return

        first_delta = asyncio.Event()

        async def read():
            async for chunk in stream:
                if "delta" in chunk:
                    first_delta.set()

        if how == "scope":
            async with anyio.create_task_group() as group:
                group.start_soon(read)
                await first_delta.wait()
                group.cancel_scope.cancel()

            return

        reading = asyncio.create_task(read())
        await first_delta.wait()
        reading.cancel()
        await asyncio.gather(reading, return_exceptions=True)

    asyncio.run(asyncio.wait_for(scenario(), 2))

    assert saved == [(Status.CANCELLED, "Half", [])]
    assert saved.tokens == [("ann", 0)]
