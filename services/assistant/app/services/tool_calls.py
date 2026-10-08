import asyncio
import time

import httpx
from prepza_common.i18n import translate

from app.constants.tool_calls import (
    INVALID_ARGUMENTS,
    MAX_PARALLEL_TOOL_CALLS,
    SERVICE_UNAVAILABLE,
    UNKNOWN_TOOL,
)
from app.helpers.arguments import fill_path, problems
from app.helpers.blocks import render_block
from app.helpers.trimming import trim
from app.integrations import services
from app.models.tools import Tool, ToolResult
from app.services.registry import tools


async def call_tools(
    calls: list[tuple[str, dict]], token: str, language: str, company_id: str | None
) -> list[ToolResult]:
    """One step's tool calls, at most MAX_PARALLEL_TOOL_CALLS at a time, in the given order."""
    gate = asyncio.Semaphore(MAX_PARALLEL_TOOL_CALLS)

    async def one(name: str, arguments: dict) -> ToolResult:
        async with gate:
            return await call_tool(name, arguments, token, language, company_id)

    return list(await asyncio.gather(*(one(name, arguments) for name, arguments in calls)))


async def call_tool(
    name: str, arguments: dict, token: str, language: str, company_id: str | None
) -> ToolResult:
    """Calls one tool as the user. Errors are results too, which the model explains: an unknown
    tool, refused arguments, the service's own error (its detail is in the user's language) or
    no answer."""
    started = time.monotonic()

    def result(status: int | None, content: dict, block: dict | None = None) -> ToolResult:
        duration = round((time.monotonic() - started) * 1000)

        return ToolResult(name, arguments, status, content, block, duration)

    tool = tools().get(name)

    if tool is None:
        return result(None, {"error": 404, "detail": translate(UNKNOWN_TOOL, language)})

    found = problems(arguments, tool.parameters)

    if found:
        detail = f"{translate(INVALID_ARGUMENTS, language)}: {'; '.join(found)}"

        return result(None, {"error": 422, "detail": detail})

    given = {key: value for key, value in arguments.items() if value is not None}
    wanted = min(given.get("limit", tool.max_items), tool.max_items)
    query = {param: given[param] for param in tool.query_params if param in given}

    # One more than wanted, to tell whether there are more.
    if "limit" in tool.query_params:
        query["limit"] = wanted + 1

    path = fill_path(tool.path, {param: given[param] for param in tool.path_params})

    try:
        response = await services.get(tool.service, path, query, token, language)
    except httpx.TimeoutException:
        return result(None, {"error": 504, "detail": translate(SERVICE_UNAVAILABLE, language)})
    except httpx.HTTPError:
        return result(None, {"error": 503, "detail": translate(SERVICE_UNAVAILABLE, language)})

    if not response.is_success:
        return result(response.status_code, error_content(response, language))

    content, data = read(tool, response, wanted)
    context = {"company_id": company_id, **given}

    return result(
        response.status_code, content, render_block(tool.render, tool.link, data, context)
    )


def read(tool: Tool, response: httpx.Response, wanted: int) -> tuple[dict, object]:
    """What the model reads of a successful answer, and the trimmed data alone."""
    is_json = response.headers.get("content-type", "").startswith("application/json")
    data = response.json() if is_json else response.text
    more = isinstance(data, list) and len(data) > wanted

    if more:
        data = data[:wanted]

    data = trim(data, tool.fields, tool.max_items, tool.max_length)
    content = {"data": data, "source": tool.name}

    if more:
        content |= {"shown": len(data), "more": True}

    return content, data


def error_content(response: httpx.Response, language: str) -> dict:
    """The service's error as the model reads it: its status and its message, already in the
    user's language (the services translate by Accept-Language)."""
    try:
        body = response.json()
    except ValueError:
        body = None

    detail = body.get("detail") if isinstance(body, dict) else None

    if not isinstance(detail, str):
        detail = (
            translate(INVALID_ARGUMENTS, language)
            if response.status_code == 422
            else response.reason_phrase
        )

    return {"error": response.status_code, "detail": detail}
