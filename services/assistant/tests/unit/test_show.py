import asyncio
import uuid

import httpx
import pytest

from app.integrations import services
from app.models.answers import Turn
from app.services.show import show

COMPANY = "8c1d2b8e-1a2b-4c3d-8e9f-0a1b2c3d4e5f"
TURN = Turn(uuid.uuid4(), "ann", uuid.UUID(COMPANY), "t", "en", frozenset({COMPANY}))
CANDIDATES = [
    {"id": "c1", "email": "ann@example.com", "status": "finished", "grade": 91, "passed": True},
    {"id": "c2", "email": "bob@example.com", "status": "finished", "grade": 40, "passed": False},
]


@pytest.fixture
def companies(monkeypatch):
    """Companies answering as the user; the paths read."""
    asked = []

    async def get(service, path, query, token, language, via=None):
        asked.append(path)
        request = httpx.Request("GET", "http://x")

        if path == "/interviews/i1/candidates":
            return httpx.Response(200, json=CANDIDATES, request=request)

        if path == "/interviews/i1":
            return httpx.Response(
                200, json={"id": "i1", "title": "Senior Backend"}, request=request
            )

        return httpx.Response(404, json={}, request=request)

    monkeypatch.setattr(services, "get", get)

    return asked


def run(arguments, shown=None):
    return asyncio.run(show(arguments, TURN, shown if shown is not None else set()))


def test_only_the_rows_the_model_chose_are_shown_and_kept_as_ids(companies):
    content, block = run(
        {"kind": "candidates", "rows": [{"interview_id": "i1", "candidate_id": "c1"}]}
    )

    assert content == {"detail": "Shown under your answer."}
    assert [item["email"] for item in block["items"]] == ["ann@example.com"]
    assert block["links"] == [f"/companies/{COMPANY}/interviews/i1/candidates/c1"]
    assert block["ref"]["refs"] == [{"id": "c1", "interview_id": "i1"}]
    assert "ann@example.com" not in str(block["ref"])


def test_a_link_is_built_from_the_app_map_and_named_by_what_it_opens(companies):
    _, block = run({"kind": "link", "page": "interview", "interview_id": "i1"})

    assert block["links"] == [f"/companies/{COMPANY}/interviews/i1"]
    assert block["label"] == "Senior Backend"
    assert block["ref"] == {
        "kind": "link",
        "page": "interview",
        "ids": {"company_id": COMPANY, "interview_id": "i1"},
        "links": [f"/companies/{COMPANY}/interviews/i1"],
    }


@pytest.mark.parametrize(
    "arguments",
    [
        {"kind": "link", "page": "https://evil.example"},
        {"kind": "link", "page": "interview", "interview_id": "../internal"},
        # An interview the user can't see.
        {"kind": "link", "page": "interview", "interview_id": "gone"},
        {"kind": "candidates", "rows": [{"interview_id": "i1", "candidate_id": "zz"}]},
    ],
)
def test_nothing_is_shown_for_an_unknown_page_bad_ids_or_what_the_user_cant_see(
    companies, arguments
):
    content, block = run(arguments)

    assert block is None
    assert content["error"] == 404


def test_one_list_and_one_link_an_answer(companies):
    shown = set()
    run({"kind": "link", "page": "pricing"}, shown)
    content, block = run({"kind": "link", "page": "faq"}, shown)

    assert block is None
    assert content["error"] == 409
    _, rows = run(
        {"kind": "candidates", "rows": [{"interview_id": "i1", "candidate_id": "c2"}]}, shown
    )
    assert rows is not None


def test_an_answer_about_one_interview_gets_its_candidates_link_when_the_model_gave_none(
    companies,
):
    from app.models.answers import Answer
    from app.models.tools import ToolResult
    from app.services.show import finish

    answer = Answer()
    answer.results.append(ToolResult("list_candidates", {"interview_id": "i1"}, 200, {}, None, 0))
    emitted = []
    asyncio.run(finish(answer, TURN, emitted.append))

    assert emitted == [
        {
            "block": {
                "kind": "link",
                "items": [],
                "links": [f"/companies/{COMPANY}/interviews/i1/candidates"],
                "page": "interview_candidates",
                "label": "Senior Backend",
            }
        }
    ]
    assert answer.blocks[0]["page"] == "interview_candidates"


def test_one_candidates_report_is_linked_and_a_single_row_shows_alone(companies):
    from app.models.answers import Answer
    from app.models.tools import ToolResult
    from app.services.show import finish

    answer = Answer()
    answer.results.append(
        ToolResult("get_scorecard", {"interview_id": "i1", "invite_id": "c1"}, 200, {}, None, 0)
    )
    emitted = []
    asyncio.run(finish(answer, TURN, emitted.append))
    assert emitted[0]["block"]["links"] == [f"/companies/{COMPANY}/interviews/i1/candidates/c1"]

    row = Answer()
    row.results = answer.results
    shown = set()
    _, rows = run(
        {"kind": "candidates", "rows": [{"interview_id": "i1", "candidate_id": "c1"}]}, shown
    )
    _, link = run(
        {"kind": "link", "page": "candidate", "interview_id": "i1", "candidate_id": "c1"}, shown
    )
    row.shown_blocks = [rows, link]
    emitted = []
    asyncio.run(finish(row, TURN, emitted.append))

    assert [event["block"]["kind"] for event in emitted] == ["candidate_rows"]


def test_no_link_is_guessed_for_an_answer_about_several_interviews(companies):
    from app.models.answers import Answer
    from app.models.tools import ToolResult
    from app.services.show import finish

    answer = Answer()
    answer.results += [
        ToolResult("list_candidates", {"interview_id": "i1"}, 200, {}, None, 0),
        ToolResult("list_candidates", {"interview_id": "i2"}, 200, {}, None, 0),
    ]
    emitted = []
    asyncio.run(finish(answer, TURN, emitted.append))

    assert emitted == []
