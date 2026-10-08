"""The tools against the running stack's services, as a throwaway Auth emulator user."""

import uuid

from app.services.tool_calls import call_tool


def test_a_tool_calls_companies_as_the_user(run, token):
    companies = run(call_tool("list_companies", {}, token, "en", None))
    pause = run(call_tool("get_pause", {}, token, "en", None))

    # A new user has no companies yet.
    assert (companies.status_code, companies.content) == (
        200,
        {"data": [], "source": "list_companies"},
    )
    assert pause.content["data"] == {"paused": False}


def test_another_companys_data_is_refused_by_companies(run, token):
    result = run(call_tool("get_company", {"company_id": str(uuid.uuid4())}, token, "de", None))

    assert result.status_code in (403, 404)
    assert result.content["error"] == result.status_code
    assert result.content["detail"]


def test_a_forged_token_is_refused_downstream(run):
    result = run(call_tool("list_companies", {}, "forged", "en", None))

    assert result.status_code == 401
