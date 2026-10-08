import uuid
from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.constants import HOUR_SECONDS
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
)
from app.constants.chat import SESSION_EXPIRED
from app.constants.limits import ACTIONS_PER_USER_HOUR
from app.helpers.arguments import problems
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
    """The confirmation card's block: the action, the arguments it shows (exactly what runs),
    whether it can't be undone, and its state."""
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


async def prepare(tool: Tool, arguments: dict, turn: Turn) -> ToolResult:
    """What the model asked for, kept (in Redis, for a short while) for the user to confirm: bound
    to them, the conversation and the company. Nothing runs yet."""
    found = problems(arguments, tool.parameters)

    if found:
        content = {"error": 422, "detail": "; ".join(found)}

        return ToolResult(tool.name, arguments, None, content, None, 0)

    action_id = uuid.uuid4()
    company_id = arguments.get("company_id") or (str(turn.company_id) if turn.company_id else None)
    pending = {
        "user_id": turn.user_id,
        "conversation_id": str(turn.conversation_id),
        "company_id": company_id,
        "tool": tool.name,
        "arguments": arguments,
    }
    await actions.save(action_id, pending)
    content = {"pending_confirmation": True, "detail": PENDING_FOR_MODEL}
    block = card(action_id, tool, arguments, PENDING)

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
        tool.name, arguments, token, language, pending["company_id"], str(action_id)
    )

    # The service refused the token: nothing ran, so it can be confirmed again once refreshed.
    if result.status_code == status.HTTP_401_UNAUTHORIZED:
        await actions.put_back(action_id, pending)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, SESSION_EXPIRED)

    links = result.block["links"] if result.succeeded and result.block else []
    state = DONE if result.succeeded else FAILED
    detail = None if result.succeeded else result.content.get("detail")

    return (
        tool,
        pending,
        result,
        card(action_id, tool, arguments, state, links=links, detail=detail),
    )
