import uuid
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from prepza_common.constants import HOUR_SECONDS
from prepza_common.i18n import translate
from prepza_common.pause import refuse_if_paused
from prepza_common.rate_limit import hit
from prepza_common.user import User

from app.constants.actions_flow import (
    ACTION_GONE,
    CANCELLED,
    DONE,
    FAILED,
    PENDING,
    PENDING_FOR_MODEL,
    SUBJECT_NOT_FOUND,
)
from app.constants.chat import SESSION_EXPIRED
from app.constants.limits import ACTIONS_PER_USER_HOUR
from app.helpers.arguments import fill_path, problems
from app.integrations import services
from app.integrations.redis import get_redis
from app.models.answers import Turn
from app.models.tools import Tool, ToolResult
from app.services import limits
from app.services.conversations import open_conversation
from app.services.registry import tools
from app.services.tenancy import require_company, user_companies
from app.services.tool_calls import call_tool
from app.storage import actions


def card(action_id: UUID, tool: Tool, arguments: dict, state: str, **more) -> dict:
    """The confirmation card's block: the action, what it's about (`subject`), the arguments it
    shows (exactly what runs), whether it can't be undone, and its state."""
    shown = {name: arguments[name] for name in tool.preview if arguments.get(name) is not None}

    return {
        "kind": "confirm",
        "items": [],
        "links": more.pop("links", []),
        "action_id": str(action_id),
        "tool": tool.name,
        "preview": shown,
        "company_id": arguments.get("company_id"),
        "destructive": tool.destructive,
        "state": state,
        **more,
    }


async def subject_of(tool: Tool, arguments: dict, token: str, language: str) -> str | None:
    """What the action is about, as the user may see it (a company's name, an interview's
    title), read with their token; raises LookupError when it's not theirs or is gone."""
    entry = tool.subject

    if entry is None:
        return None

    path = fill_path(entry["path"], arguments)
    query = {name: arguments[name] for name in entry.get("query", []) if name in arguments}

    try:
        response = await services.get(entry["service"], path, query, token, language)
    except httpx.HTTPError:
        return None

    if not response.is_success:
        raise LookupError

    data = response.json()

    if isinstance(data, list):
        wanted = str(arguments[entry["match"]])
        data = next((item for item in data if str(item.get("id")) == wanted), None)

        if data is None:
            raise LookupError

    return data.get(entry["field"]) if isinstance(data, dict) else None


async def prepare(tool: Tool, arguments: dict, turn: Turn) -> ToolResult:
    """What the model asked for, kept (in Redis, for a short while) for the user to confirm: bound
    to them, the conversation and the company. Nothing runs yet; what it's about is read with
    the user's token to name it on the card, and must be theirs to see."""
    found = problems(arguments, tool.parameters)

    if found:
        content = {"error": 422, "detail": "; ".join(found)}

        return ToolResult(tool.name, arguments, None, content, None, 0)

    try:
        subject = await subject_of(tool, arguments, turn.token, turn.language)
    except LookupError:
        content = {"error": 404, "detail": translate(SUBJECT_NOT_FOUND, turn.language)}

        return ToolResult(tool.name, arguments, None, content, None, 0)

    action_id = uuid.uuid4()
    company_id = arguments.get("company_id")
    block = card(action_id, tool, arguments, PENDING, subject=subject)
    pending = {
        "user_id": turn.user_id,
        "conversation_id": str(turn.conversation_id),
        # The company it changes (checked again on confirm), and the panel's company, for the
        # link its result opens.
        "company_id": company_id,
        "context_company_id": company_id or (str(turn.company_id) if turn.company_id else None),
        "tool": tool.name,
        "arguments": arguments,
        "card": block,
    }
    await actions.save(action_id, pending)
    content = {"pending_confirmation": True, "detail": PENDING_FOR_MODEL}

    return ToolResult(tool.name, arguments, None, content, block, 0, action_id)


async def owned_action(
    conversation_id: UUID, action_id: UUID, user: User, token: str, language: str
) -> dict:
    """The pending action, when it's this user's, in this conversation, about a company that's
    still theirs (checked with their current token); a 404 otherwise, and a 409 once it's gone
    (handled, or expired)."""
    await open_conversation(conversation_id, user.uid, token, language)
    pending = await actions.peek(action_id)

    # Handled already, or expired.
    if pending is None:
        raise HTTPException(status.HTTP_409_CONFLICT, ACTION_GONE)

    if pending["user_id"] != user.uid or pending["conversation_id"] != str(conversation_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, ACTION_GONE)

    require_company(pending["company_id"], await user_companies(token, language))

    return pending


async def claim(action_id: UUID) -> dict:
    """Takes the action for this request alone: a second confirm (or a cancel) finds it gone."""
    pending = await actions.claim(action_id)

    if pending is None:
        raise HTTPException(status.HTTP_409_CONFLICT, ACTION_GONE)

    return pending


async def cancel(conversation_id: UUID, action_id: UUID, user: User, token, language) -> dict:
    """Drops the action; the card shows it cancelled."""
    await owned_action(conversation_id, action_id, user, token, language)
    await claim(action_id)

    return {"action_id": str(action_id), "state": CANCELLED}


async def run(
    conversation_id: UUID, action_id: UUID, user: User, token: str, language: str
) -> tuple[Tool, dict, ToolResult, dict]:
    """Runs the action once, as the user, with exactly the arguments the card showed: the tool,
    the user's companies, its result and the card's new state."""
    redis = get_redis()
    await refuse_if_paused(redis)
    pending = await owned_action(conversation_id, action_id, user, token, language)
    company_id = UUID(pending["company_id"]) if pending["company_id"] else None
    await hit(redis, f"rate:assistant:actions:{user.uid}", ACTIONS_PER_USER_HOUR, HOUR_SECONDS)
    await limits.check(redis, user.uid, company_id)
    pending = await claim(action_id)
    tool = tools()[pending["tool"]]
    arguments = pending["arguments"]
    result = await call_tool(
        tool.name, arguments, token, language, pending["context_company_id"], str(action_id)
    )

    # The service refused the token: nothing ran, so it can be confirmed again once refreshed.
    if result.status_code == status.HTTP_401_UNAUTHORIZED:
        await actions.put_back(action_id, pending)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_EXPIRED)

    done = result.succeeded
    data = result.content.get("data") if done else None
    label = data.get(tool.result_label) if tool.result_label and isinstance(data, dict) else None
    block = {
        **pending["card"],
        "state": DONE if done else FAILED,
        "links": result.block["links"] if done and result.block else [],
        "result_label": label,
        "detail": None if done else result.content.get("detail"),
    }

    return tool, pending, result, block
