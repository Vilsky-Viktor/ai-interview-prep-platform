import asyncio
import uuid

import pytest
from fastapi import HTTPException, status

from app.integrations import greenhouse, workable
from app.integrations.errors import KeyRejected
from app.models.ats import AtsCandidate, AtsConnection
from app.services import ats as integrations
from app.services import ats_candidates as flow
from app.storage import ats, ats_candidates

INTERVIEW_ID = uuid.uuid4()
COMPANY_ID = uuid.uuid4()
KEYS = {
    "workable": {"subdomain": "acme", "token": "account-token"},
    "greenhouse": {"client_id": "id", "client_secret": "secret", "webhook_secret": "s"},
}


@pytest.fixture
def finished(monkeypatch):
    """A candidate the ATS sent who finished with 82%, and comments (Workable) or notes
    (Greenhouse) recorded instead of sent. The connection is Workable's, with a member."""
    connection = AtsConnection(
        id=uuid.uuid4(), provider="workable", status="connected", member_id="m-1"
    )
    row = AtsCandidate(id=uuid.uuid4(), candidate_id="c-1", invite_id=uuid.uuid4())
    state = {"comments": [], "reported": [], "broken": [], "fail": None, "row": row}

    async def for_invite(invite_id):
        return (row, connection) if invite_id == row.invite_id else None

    async def key(found):
        return KEYS[found.provider]

    async def comment(candidate_id, member, text, **credentials):
        if state["fail"]:
            raise state["fail"]

        state["comments"].append((candidate_id, member, text))

    async def mark_reported(row_id):
        state["reported"].append(row_id)

    async def mark_broken(connection_id):
        state["broken"].append(connection_id)

    monkeypatch.setattr(ats_candidates, "for_invite", for_invite)
    monkeypatch.setattr(ats_candidates, "mark_reported", mark_reported)
    monkeypatch.setattr(ats, "mark_broken", mark_broken)
    monkeypatch.setattr(integrations, "credentials", key)
    monkeypatch.setattr(workable, "comment", comment)
    monkeypatch.setattr(greenhouse, "comment", comment)

    return state, connection


def report(invite_id, grade=82, passed=True):
    """Companies' candidate.finished event, as it carries the result."""
    data = {
        "candidate_invite_id": str(invite_id),
        "interview_id": str(INTERVIEW_ID),
        "company_id": str(COMPANY_ID),
        "title": "Accountant",
        "grade": grade,
        "passed": passed,
        "flagged": False,
    }
    asyncio.run(flow.report(data))


def test_results_go_back_to_workable_once_as_a_comment(finished):
    state, _ = finished
    report(state["row"].invite_id)

    [(candidate_id, member, text)] = state["comments"]
    assert (candidate_id, member) == ("c-1", "m-1")
    assert "prepza: Accountant" in text
    assert "Grade: 82% (passed)" in text
    assert text.endswith(
        f"http://localhost:8090/companies/{COMPANY_ID}/interviews/{INTERVIEW_ID}"
        f"/candidates/{state['row'].invite_id}"
    )
    assert state["reported"] == [state["row"].id]


def test_a_candidate_no_ats_sent_is_ignored(finished):
    state, _ = finished
    report(uuid.uuid4())

    assert state["comments"] == [] and state["reported"] == []


def test_without_a_workable_member_nothing_goes_back(finished):
    state, connection = finished
    connection.member_id = None
    report(state["row"].invite_id)

    assert state["comments"] == []


def test_a_failing_workable_raises_so_the_event_comes_again(finished):
    state, _ = finished
    state["fail"] = HTTPException(status.HTTP_502_BAD_GATEWAY, "down")

    with pytest.raises(HTTPException):
        report(state["row"].invite_id)

    assert state["reported"] == []


def test_a_refused_key_marks_the_connection_broken_and_gives_up(finished):
    state, _ = finished
    state["fail"] = KeyRejected()
    report(state["row"].invite_id)

    assert len(state["broken"]) == 1
    assert state["reported"] == []


def test_results_go_back_to_greenhouse_as_a_note_without_a_member(finished):
    state, connection = finished
    connection.provider, connection.member_id = "greenhouse", None
    report(state["row"].invite_id, grade=None, passed=False)

    [(candidate_id, member, text)] = state["comments"]
    assert (candidate_id, member) == ("c-1", None)
    assert "the grade is on the scorecard" in text
    assert state["reported"] == [state["row"].id]
