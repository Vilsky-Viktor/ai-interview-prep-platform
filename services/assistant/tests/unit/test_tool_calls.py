import asyncio

import httpx
import pytest

from app.integrations import services
from app.services.tool_calls import call_tool, call_tools

COMPANY = "8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f"
INTERVIEW = "3f2b6a1e-8a7c-4c1e-9a55-0b6f3c2d1e00"


def answer(status=200, json=None, text=None, headers=None):
    request = httpx.Request("GET", "http://service")

    if json is not None:
        return httpx.Response(status, json=json, request=request)

    return httpx.Response(status, text=text or "", headers=headers, request=request)


class Calls(list):
    """The GETs made, and what the service answers (`answer`)."""

    answer = None


@pytest.fixture
def calls(monkeypatch):
    """Records each GET the tools make; the test sets what the service answers."""
    made = Calls()
    made.answer = answer(json=[])

    async def fake_get(service, path, query, token, language):
        made.append((service, path, query, token, language))
        found = made.answer

        if isinstance(found, Exception):
            raise found

        return found

    monkeypatch.setattr(services, "get", fake_get)

    return made


def run(name, arguments, company_id=COMPANY):
    return asyncio.run(call_tool(name, arguments, "user-token", "de", company_id))


def test_a_list_is_trimmed_cut_and_shown_as_linked_rows(calls):
    rows = [
        {"id": f"c{i}", "email": f"c{i}@example.com", "grade": 80, "passed": None, "secret": "x"}
        for i in range(4)
    ]
    calls.answer = answer(json=rows)
    result = run("list_candidates", {"interview_id": INTERVIEW, "status": "finished", "limit": 3})

    # One more than wanted, to tell whether there are more.
    assert calls == [
        (
            "companies",
            f"/interviews/{INTERVIEW}/candidates",
            {"status": "finished", "limit": 4},
            "user-token",
            "de",
        )
    ]
    assert result.status_code == 200
    assert result.content == {
        "data": [{"id": f"c{i}", "email": f"c{i}@example.com", "grade": 80} for i in range(3)],
        "source": "list_candidates",
        "shown": 3,
        "more": True,
    }
    assert result.block["kind"] == "candidate_rows"
    assert result.block["links"][0] == (
        f"/companies/{COMPANY}/interviews/{INTERVIEW}/candidates/c0"
    )


def test_a_limit_is_capped_at_the_tools_maximum_and_set_when_left_out(calls):
    run("list_interviews", {"company_id": COMPANY})

    assert calls[0][2] == {"company_id": COMPANY, "limit": 21}
    assert run("list_interviews", {"company_id": COMPANY, "limit": 50}).status_code is None


def test_the_platform_guide_is_read_whole_as_text(calls):
    guide = "<guide>\n" + "How prepza works. " * 2_000
    calls.answer = answer(text=guide, headers={"content-type": "text/plain"})
    result = run("get_platform_guide", {})

    assert calls[0][:3] == ("rounds", "/help/guide", {})
    assert result.content == {"data": guide, "source": "get_platform_guide"}
    assert result.block == {"kind": "link", "items": [], "links": ["/faq"]}


def test_a_services_error_reaches_the_model_in_the_users_language(calls):
    calls.answer = answer(403, json={"detail": "Keine Berechtigung"})

    result = run("get_company", {"company_id": COMPANY})

    assert result.status_code == 403
    assert result.content == {"error": 403, "detail": "Keine Berechtigung"}
    assert result.block is None


def test_errors_without_a_message_name_their_status(calls):
    calls.answer = answer(422, json={"detail": [{"msg": "bad"}]})
    assert run("get_pause", {}).content["error"] == 422

    calls.answer = answer(502, text="<html>")
    assert run("get_pause", {}).content == {"error": 502, "detail": "Bad Gateway"}


@pytest.mark.parametrize(
    "error, status",
    [(httpx.ReadTimeout("slow"), 504), (httpx.ConnectError("down"), 503)],
)
def test_a_service_that_doesnt_answer_is_an_error_too(calls, error, status):
    calls.answer = error
    result = run("get_pause", {})

    assert result.status_code is None
    assert result.content["error"] == status
    assert result.content["detail"]


def test_refused_arguments_and_unknown_tools_call_nothing(calls):
    bad = run("get_company", {"company_id": "../internal/users"})
    unknown = run("delete_company", {"company_id": COMPANY})

    assert calls == []
    assert bad.content["error"] == 422
    assert "company_id must be a UUID" in bad.content["detail"]
    assert unknown.content["error"] == 404


def test_a_steps_calls_run_at_most_four_at_a_time_in_order(monkeypatch):
    running, most = 0, 0

    async def fake_get(service, path, query, token, language):
        nonlocal running, most
        running += 1
        most = max(most, running)
        await asyncio.sleep(0.01)
        running -= 1

        return answer(json={"paused": False})

    monkeypatch.setattr(services, "get", fake_get)
    names = ["get_pause"] * 7 + ["get_me"]
    results = asyncio.run(call_tools([(name, {}) for name in names], "t", "en", None))

    assert most == 4
    assert [result.tool for result in results] == names
