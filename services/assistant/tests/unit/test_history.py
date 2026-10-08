import json
import uuid

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.helpers.history import history
from app.models.conversations import Message, ToolCall


def message(role, content):
    return Message(id=uuid.uuid4(), role=role, content=content)


def call(tool, result):
    return ToolCall(id=uuid.uuid4(), tool=tool, arguments={"q": "x"}, result=result)


def test_an_answer_comes_back_with_the_tools_it_called_and_their_results():
    found = call("get_pause", {"data": {"paused": False}})
    rows = [
        (message("user", "Paused?"), []),
        (message("assistant", "No."), [found]),
    ]

    assert history(rows, 1_000) == [
        HumanMessage(content="Paused?"),
        AIMessage(
            content="", tool_calls=[{"name": "get_pause", "args": {"q": "x"}, "id": str(found.id)}]
        ),
        ToolMessage(content=json.dumps(found.result), tool_call_id=str(found.id)),
        AIMessage(content="No."),
    ]


def test_only_the_latest_messages_that_fit_are_kept_and_big_results_drop_first():
    guide = call("get_platform_guide", {"data": "x" * 500})
    rows = [
        (message("user", "a" * 50), []),
        (message("assistant", "b" * 50), []),
        (message("user", "How do I invite?"), []),
        (message("assistant", "From the interview's page."), [guide]),
    ]

    kept = history(rows, 100)

    # The answer keeps its text without the guide; the oldest message no longer fits.
    assert kept == [
        AIMessage(content="b" * 50),
        HumanMessage(content="How do I invite?"),
        AIMessage(content="From the interview's page."),
    ]


def test_a_failed_answer_without_text_or_tools_adds_nothing():
    rows = [(message("user", "Hi"), []), (message("assistant", ""), [])]

    assert history(rows, 1_000) == [HumanMessage(content="Hi")]
