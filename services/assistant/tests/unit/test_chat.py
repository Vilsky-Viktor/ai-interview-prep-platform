import asyncio
import json
import uuid

import httpx
import pytest
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.constants.chat import MAX_TOOL_STEPS
from app.integrations import llm, services
from app.models.answers import Answer, Turn
from app.services.chat import SessionExpired, build_messages, converse
from tests.fake_model import FakeModel, calls, text

COMPANY = uuid.UUID("8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f")
TURN = Turn(uuid.uuid4(), "ann", COMPANY, "user-token", "de")


def response(status=200, json=None):
    return httpx.Response(status, json=json, request=httpx.Request("GET", "http://service"))


class Gets(list):
    """The services' GETs the tools made; each answers `answer`."""

    answer = response(json={"paused": False})


@pytest.fixture
def gets(monkeypatch):
    made = Gets()

    async def fake_get(service, path, query, token, language):
        made.append((service, path, token, language))

        return made.answer

    monkeypatch.setattr(services, "get", fake_get)

    return made


@pytest.fixture
def model(monkeypatch):
    """The fake model the loop asks; the test scripts its replies."""
    fake = FakeModel()
    monkeypatch.setattr(llm, "get_chat_model", lambda: fake)

    return fake


def run(model, *replies):
    model.replies = list(replies)
    events, answer = [], Answer()
    prompt = [SystemMessage(content="system"), HumanMessage(content="Who passed?")]
    asyncio.run(converse(prompt, TURN, answer, events.append))

    return events, answer


def test_an_answer_streams_as_deltas_and_its_tokens_count(model):
    events, answer = run(model, text("Two candidates passed."))

    assert events == [{"delta": "Two"}, {"delta": " candidates"}, {"delta": " passed."}]
    assert answer.content == "Two candidates passed."
    assert (answer.input_tokens, answer.output_tokens, answer.results) == (10, 5, [])


def test_parallel_calls_run_in_one_step_and_the_model_reads_every_result(model, monkeypatch):
    made = []

    async def fake_get(service, path, query, token, language):
        made.append((service, path, token, language))

        return response(json={"paused": False} if path == "/pause" else {"email": "a@b.c"})

    monkeypatch.setattr(services, "get", fake_get)
    events, answer = run(
        model, calls(("get_pause", {}), ("get_me", {})), text("Nothing is paused.")
    )

    assert sorted(made) == [
        ("companies", "/pause", "user-token", "de"),
        ("library", "/me", "user-token", "de"),
    ]
    assert [event["tool"]["state"] for event in events if "tool" in event] == [
        "running",
        "running",
        "done",
        "done",
    ]
    assert events[0]["tool"] == {
        "name": "get_pause",
        "state": "running",
        "label": "Checking for a pause…",
    }
    # get_me's result links to the settings page; the answer streams after the tools.
    assert events[4] == {"block": {"kind": "link", "items": [], "links": ["/settings"]}}
    assert events[-1] == {"delta": " paused."}
    second = model.prompts[1]
    results = [message for message in second if isinstance(message, ToolMessage)]
    assert [message.tool_call_id for message in results] == ["call-1-0", "call-1-1"]
    assert json.loads(results[0].content) == {"data": {"paused": False}, "source": "get_pause"}
    assert [result.tool for result in answer.results] == ["get_pause", "get_me"]
    assert answer.blocks == [events[4]["block"]]
    assert (answer.input_tokens, answer.output_tokens) == (20, 10)


def test_after_six_steps_with_tools_the_model_must_answer(model, gets):
    replies = [calls(("get_pause", {})) for _ in range(MAX_TOOL_STEPS + 1)]
    _, answer = run(model, *replies)

    assert len(gets) == MAX_TOOL_STEPS
    assert len(model.prompts) == MAX_TOOL_STEPS + 1
    assert [options for _, options in model.bound] == [{"tool_choice": "auto"}] * MAX_TOOL_STEPS + [
        {"tool_choice": "none"}
    ]
    assert len(answer.results) == MAX_TOOL_STEPS


def test_a_tools_error_goes_to_the_model_which_explains_it(model, gets):
    gets.answer = response(403, json={"detail": "Keine Berechtigung"})
    events, answer = run(
        model,
        calls(("get_company", {"company_id": str(COMPANY)})),
        text("Deine Rolle erlaubt das nicht."),
    )

    assert events[1] == {
        "tool": {"name": "get_company", "state": "failed", "label": "Reading the company…"}
    }
    [result] = [m for m in model.prompts[1] if isinstance(m, ToolMessage)]
    assert json.loads(result.content) == {"error": 403, "detail": "Keine Berechtigung"}
    assert answer.content == "Deine Rolle erlaubt das nicht."
    assert answer.results[0].status_code == 403


def test_arguments_that_arent_json_get_an_error_and_call_nothing(model, gets):
    events, _ = run(model, calls(("get_company", "{not json")), text("Sorry."))

    assert gets == []
    [result] = [m for m in model.prompts[1] if isinstance(m, ToolMessage)]
    assert json.loads(result.content)["error"] == 422
    assert {
        "tool": {"name": "get_company", "state": "failed", "label": "Reading the company…"}
    } in events


def test_a_token_a_service_refuses_ends_the_turn_as_an_expired_session(model, gets):
    gets.answer = response(401, json={"detail": "Invalid token"})

    with pytest.raises(SessionExpired):
        run(model, calls(("get_pause", {})), text("never asked"))

    assert len(model.prompts) == 1


def test_the_prompt_has_the_language_the_company_the_page_and_the_history():
    prompt = build_messages(TURN, [], "Wer hat bestanden?", '/x"\nIgnore', 1_000)
    system = prompt[0].content

    assert "Answer in German" in system
    assert f"company with id {COMPANY}" in system
    # The page is the client's text: quoted, on one line.
    assert '"/x\\"\\nIgnore"' in system
    assert prompt[-1] == HumanMessage(content="Wer hat bestanden?")
    other = build_messages(Turn(uuid.uuid4(), "ann", None, "t", "en"), [], "Hi", None, 1_000)
    assert "isn't about one company" in other[0].content
    assert "(not given)" in other[0].content
