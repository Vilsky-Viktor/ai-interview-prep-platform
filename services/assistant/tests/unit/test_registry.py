import pytest

from app.constants.tool_calls import FORBIDDEN_PATH_PREFIXES
from app.constants.tools import TOOLS
from app.services.registry import build, tools


def test_every_tool_resolves_in_its_services_snapshot():
    built = tools()

    assert set(built) == set(TOOLS)
    assert {"search_candidates", "get_platform_guide", "get_api_settings"} <= set(built)


@pytest.mark.parametrize("name", sorted(TOOLS))
def test_every_tool_is_a_user_facing_get(name):
    entry = TOOLS[name]

    assert entry["method"] == "GET"
    assert not entry["path"].startswith(FORBIDDEN_PATH_PREFIXES)


@pytest.mark.parametrize(
    "change, problem",
    [
        ({"method": "POST"}, "only GET"),
        ({"method": "DELETE"}, "only GET"),
        ({"path": "/internal/users/{user_id}"}, "not a user-facing route"),
        ({"path": "/superadmin/companies"}, "not a user-facing route"),
        ({"path": "/nowhere"}, "has no GET /nowhere"),
        ({"params": ["company_id", "nope"]}, "no parameter nope"),
        ({"params": []}, "required parameters not allowed"),
        ({"service": "elsewhere"}, "unknown service"),
    ],
)
def test_the_loader_refuses_what_the_assistant_must_not_call(change, problem):
    entry = {**TOOLS["get_company"], **change}

    with pytest.raises(ValueError, match=problem):
        build("get_company", entry)


def test_a_route_gone_from_the_snapshot_stops_the_start(monkeypatch):
    monkeypatch.setitem(TOOLS, "gone", {**TOOLS["get_pause"], "path": "/gone"})
    tools.cache_clear()

    try:
        with pytest.raises(ValueError, match="has no GET /gone"):
            tools()
    finally:
        monkeypatch.delitem(TOOLS, "gone")
        tools.cache_clear()


def test_parameters_keep_the_routes_types_enums_and_bounds():
    tool = tools()["list_candidates"]
    properties = tool.parameters["properties"]

    assert tool.path_params == ("interview_id",)
    assert tool.query_params == ("q", "status", "sort", "offset", "limit")
    assert tool.parameters["required"] == ["interview_id"]
    assert tool.parameters["additionalProperties"] is False
    assert properties["interview_id"] == {"type": "string", "format": "uuid"}
    assert properties["q"] == {"type": "string", "maxLength": 254}
    assert "finished" in properties["status"]["enum"]
    assert properties["sort"]["enum"] == ["grade", "date"]
    # `limit` is capped at what the model may read.
    assert properties["limit"]["maximum"] == tool.max_items == 20


def test_a_tool_is_described_by_its_route_or_its_override():
    built = tools()

    assert (
        built["get_platform_guide"]
        .definition["function"]["description"]
        .startswith("Everything prepza's help knows")
    )
    assert built["list_interviews"].definition["function"]["description"]
    assert built["get_api_settings"].path == "/manage"
