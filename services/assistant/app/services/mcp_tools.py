import json
import logging
import uuid
from datetime import UTC, datetime

import mcp_types as types
from fastapi import HTTPException
from prepza_common.analytics import track
from prepza_common.constants import DAY_SECONDS, MINUTE_SECONDS
from prepza_common.i18n import translate
from prepza_common.pause import refuse_if_paused
from prepza_common.rate_limit import hit_or_skip
from prepza_common.secrets_check import SECRET_REMOVED, secret_in
from prepza_common.user import User

from app.config.settings import settings
from app.constants.chat import COMPANY_NOT_FOUND
from app.constants.limits import (
    MCP_CALLS_PER_USER_DAY,
    MCP_CALLS_PER_USER_MINUTE,
)
from app.constants.mcp import (
    ACCOUNT_GONE,
    ACTIVE_KEY,
    EXCLUDED_TOOL,
    MCP_EXCLUDED,
    MCP_UNLISTED,
    UPDATE_LANGUAGE,
)
from app.constants.tool_calls import UNKNOWN_TOOL, VIA_MCP
from app.helpers.mcp_schema import mcp_tool
from app.helpers.oauth import funnel_client
from app.integrations import firebase_tokens
from app.integrations.redis import get_redis
from app.models.oauth_tokens import Access
from app.models.tools import Tool
from app.services.actions import checked_arguments, count_action
from app.services.registry import tools
from app.services.tenancy import foreign_company, user_companies
from app.services.tool_calls import call_tool
from app.storage import oauth

logger = logging.getLogger(__name__)


def listed() -> list[types.Tool]:
    """Every tool an AI app may call."""
    return [
        mcp_tool(tool) for name, tool in tools().items() if name not in MCP_EXCLUDED | MCP_UNLISTED
    ]


def text_result(content: dict, error: bool) -> types.CallToolResult:
    text = json.dumps(content, ensure_ascii=False, default=str)

    return types.CallToolResult(content=[types.TextContent(text=text)], is_error=error)


def error_result(detail: str) -> types.CallToolResult:
    return text_result({"error": detail}, True)


async def count_call(user_id: str) -> None:
    """Counts one call of the user's apps; over a limit, a 429. With Redis down, not counted."""
    redis = get_redis()
    minute = f"rate:assistant:mcp:minute:{user_id}"
    await hit_or_skip(redis, minute, MCP_CALLS_PER_USER_MINUTE, MINUTE_SECONDS)
    day = f"rate:assistant:mcp:day:{user_id}"
    await hit_or_skip(redis, day, MCP_CALLS_PER_USER_DAY, DAY_SECONDS)


async def mark_active(access: Access) -> None:
    """The connection's last use, and the funnel's mcp_active once a day for each user and app.
    Neither ever fails the call."""
    client = funnel_client(access.client_name)

    try:
        await oauth.used(uuid.UUID(access.grant_id), datetime.now(UTC))
        key = ACTIVE_KEY.format(user_id=access.subject, client=client)

        if await get_redis().set(key, 1, ex=DAY_SECONDS, nx=True):
            await track("mcp_active", user_id=access.subject, client=client)
    except Exception:
        logger.warning("Couldn't record an AI app's use", exc_info=True)


async def checked_write(tool: Tool, arguments: dict, user: User, token: str) -> dict:
    """A write's arguments once it may run, as in the app: nothing while paused, about something
    the user may see, with only what changes, within their hourly actions. Otherwise an
    HTTPException saying why not."""
    redis = get_redis()
    await refuse_if_paused(redis)
    arguments, _ = await checked_arguments(tool, arguments, token, user.language)
    await count_action(redis, user.uid)

    return arguments


async def call(name: str, arguments: dict, access: Access) -> types.CallToolResult:
    """One tool, called by an AI app as the user it acts for. A write runs at once: the app asked
    the user before calling it. Its result is the data as JSON, with links to prepza's pages;
    an error is a result too, which the app explains."""
    tool = tools().get(name) if name not in MCP_UNLISTED else None

    if name in MCP_EXCLUDED:
        return error_result(EXCLUDED_TOOL)

    if tool is None:
        return error_result(UNKNOWN_TOOL)

    signed_in = await firebase_tokens.sign_in(access.subject)

    if signed_in is None:
        return error_result(ACCOUNT_GONE)

    user, token = signed_in
    texts = [value for value in arguments.values() if isinstance(value, str)]

    # Secrets are never sent through an AI app: entered in prepza itself only.
    if secret_in(texts) is not None:
        return error_result(translate(SECRET_REMOVED, user.language))

    try:
        await count_call(user.uid)
        await mark_active(access)

        # As in the app's panel: a company that isn't one of the user's isn't called at all.
        if foreign_company(arguments, await user_companies(user.uid)):
            return error_result(translate(COMPANY_NOT_FOUND, user.language))

        if tool.method != "GET":
            arguments = await checked_write(tool, arguments, user, token)
    except HTTPException as error:
        return error_result(translate(str(error.detail), user.language))

    result = await call_tool(
        name,
        arguments,
        token,
        user.language,
        arguments.get("company_id"),
        str(uuid.uuid4()) if tool.method != "GET" else None,
        via=VIA_MCP,
    )

    if tool.method != "GET":
        await track("mcp_action", user_id=user.uid, tool=name, ok=result.succeeded)

    if name == UPDATE_LANGUAGE and result.succeeded:
        firebase_tokens.forget(user.uid)

    if not result.succeeded:
        return error_result(result.content["detail"])

    site = settings.site_url.rstrip("/")
    links = [site + link for link in (result.block or {}).get("links", []) if link]
    content = {**result.content, "links": links} if links else result.content

    return text_result(content, False)
