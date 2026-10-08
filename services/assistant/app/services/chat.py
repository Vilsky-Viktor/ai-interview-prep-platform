import json
from collections.abc import Callable
from datetime import UTC, datetime

from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from prepza_common.constants import LANGUAGES
from prepza_common.i18n import translate

from app.constants.chat import MAX_TOOL_STEPS, ToolState
from app.constants.tool_calls import INVALID_ARGUMENTS
from app.constants.tool_labels import TOOL_LABELS, UNKNOWN_TOOL_LABEL
from app.helpers.history import history
from app.integrations import llm
from app.models.answers import Answer, Turn
from app.prompts.assistant import (
    ASSISTANT_SYSTEM,
    COMPANY_CONTEXT,
    NO_COMPANY_CONTEXT,
    UNKNOWN_PAGE,
)
from app.services.registry import tools
from app.services.tool_calls import call_tools

# Each event the turn sends the panel goes through one of these.
Emit = Callable[[dict], None]


class SessionExpired(Exception):
    """A service refused the user's token mid-turn."""


def build_messages(
    turn: Turn, earlier: list, message: str, page: str | None, room: int
) -> list[BaseMessage]:
    """The instructions, the conversation's latest messages within `room` characters (see
    helpers/history.py) and the new message."""
    company = (
        COMPANY_CONTEXT.format(company_id=turn.company_id)
        if turn.company_id
        else NO_COMPANY_CONTEXT
    )
    system = ASSISTANT_SYSTEM.format(
        language=LANGUAGES[turn.language],
        today=datetime.now(UTC).date().isoformat(),
        company=company,
        # Quoted: the page is the client's text.
        page=json.dumps(page) if page else UNKNOWN_PAGE,
    )

    return [SystemMessage(content=system), *history(earlier, room), HumanMessage(content=message)]


async def converse(messages: list[BaseMessage], turn: Turn, answer: Answer, emit: Emit) -> None:
    """Asks the model, runs the tools it calls and asks again with their results, streaming its
    text, until it answers without tools. After MAX_TOOL_STEPS steps with tools, it must answer
    with what it has."""
    definitions = [tool.definition for tool in tools().values()]
    model = llm.get_chat_model()

    for step in range(MAX_TOOL_STEPS + 1):
        last = step == MAX_TOOL_STEPS
        bound = model.bind_tools(definitions, tool_choice="none" if last else "auto")
        reply = await ask(bound, messages, answer, emit)
        calls = [*reply.tool_calls, *reply.invalid_tool_calls]

        if last or not calls:
            return

        messages.append(reply)
        messages += await run_tools(calls, turn, answer, emit)


async def ask(model, messages: list[BaseMessage], answer: Answer, emit: Emit) -> AIMessageChunk:
    """One model call: its text streams to the panel as it comes; its tokens are counted."""
    reply = AIMessageChunk(content="")

    async for chunk in model.astream(messages):
        reply += chunk

        if chunk.text:
            answer.parts.append(chunk.text)
            emit({"delta": chunk.text})

    if reply.usage_metadata:
        answer.input_tokens += reply.usage_metadata["input_tokens"]
        answer.output_tokens += reply.usage_metadata["output_tokens"]

    return reply


def tool_event(name: str, state: ToolState, language: str) -> dict:
    label = translate(TOOL_LABELS.get(name, UNKNOWN_TOOL_LABEL), language)

    return {"tool": {"name": name, "state": state, "label": label}}


async def run_tools(calls: list[dict], turn: Turn, answer: Answer, emit: Emit) -> list[ToolMessage]:
    """One step's tool calls, at once; their results for the model, and their progress and
    blocks for the panel. A call whose arguments aren't JSON gets an error the model can fix."""
    for call in calls:
        emit(tool_event(call["name"], ToolState.RUNNING, turn.language))

    valid = [call for call in calls if call.get("type") == "tool_call"]
    results = await call_tools(
        [(call["name"], call["args"]) for call in valid],
        turn.token,
        turn.language,
        str(turn.company_id) if turn.company_id else None,
    )
    replies = []

    for call, result in zip(valid, results, strict=True):
        state = ToolState.DONE if result.succeeded else ToolState.FAILED
        answer.results.append(result)
        emit(tool_event(call["name"], state, turn.language))

        if result.block is not None:
            answer.blocks.append(result.block)
            emit({"block": result.block})

        content = json.dumps(result.content, ensure_ascii=False)
        replies.append(ToolMessage(content=content, tool_call_id=call["id"]))

    for call in calls:
        if call.get("type") != "tool_call":
            emit(tool_event(call.get("name") or "", ToolState.FAILED, turn.language))
            error = {"error": 422, "detail": translate(INVALID_ARGUMENTS, turn.language)}
            replies.append(ToolMessage(content=json.dumps(error), tool_call_id=call["id"]))

    if any(result.status_code == 401 for result in results):
        raise SessionExpired

    return replies
