import asyncio
import uuid

import pytest
from fastapi import HTTPException, status

from app.integrations import workable
from app.models.ats import AtsCandidate, AtsConnection
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services import ats as integrations
from app.services import ats_candidates as flow
from app.storage import ats, ats_candidates, interviews, invites

TOKEN = "account-token"
# The real handler: the shared fixtures replace it, so finishing doesn't call an ATS.
REAL_REPORT = flow.report
INTERVIEW_ID = uuid.uuid4()


@pytest.fixture
def finished(monkeypatch):
    """A candidate the ATS sent who finished with 82%, and comments recorded instead of sent."""
    monkeypatch.setattr(flow, "report", REAL_REPORT)
    connection = AtsConnection(
        id=uuid.uuid4(), provider="workable", status="connected", member_id="m-1"
    )
    row = AtsCandidate(id=uuid.uuid4(), candidate_id="c-1", invite_id=uuid.uuid4())
    sent = CandidateInvite(id=row.invite_id, grade=82, flagged=False)
    interview = Interview(
        id=INTERVIEW_ID, company_id=uuid.uuid4(), title="Accountant", pass_mark=70
    )
    state = {"comments": [], "reported": [], "broken": [], "fail": None}

    async def for_invite(invite_id):
        return (row, connection) if invite_id == row.invite_id else None

    async def key(found):
        return {"subdomain": "acme", "token": TOKEN}

    async def comment(subdomain, token, candidate_id, member, text):
        if state["fail"]:
            raise state["fail"]

        state["comments"].append((candidate_id, member, text))

    async def mark_reported(row_id):
        state["reported"].append(row_id)

    async def mark_broken(connection_id):
        state["broken"].append(connection_id)

    async def get_invite(invite_id):
        return sent

    async def get_interview(interview_id):
        return interview

    monkeypatch.setattr(ats_candidates, "for_invite", for_invite)
    monkeypatch.setattr(ats_candidates, "mark_reported", mark_reported)
    monkeypatch.setattr(ats, "mark_broken", mark_broken)
    monkeypatch.setattr(integrations, "credentials", key)
    monkeypatch.setattr(workable, "comment", comment)
    monkeypatch.setattr(invites, "get", get_invite)
    monkeypatch.setattr(interviews, "get", get_interview)

    return state, row


def report(row):
    data = {"candidate_invite_id": str(row.invite_id), "answered": 3}
    asyncio.run(flow.report("interview.finished", data))


def test_results_go_back_to_workable_once_as_a_comment(finished):
    state, row = finished
    report(row)

    [(candidate_id, member, text)] = state["comments"]
    assert (candidate_id, member) == ("c-1", "m-1")
    assert "Grade: 82% (passed)" in text
    assert f"/candidates/{row.invite_id}" in text
    assert state["reported"] == [row.id]


def test_a_failing_workable_raises_so_the_event_comes_again(finished):
    state, row = finished
    state["fail"] = HTTPException(status.HTTP_502_BAD_GATEWAY, "down")

    with pytest.raises(HTTPException):
        report(row)

    assert state["reported"] == []


def test_a_refused_key_marks_the_connection_broken_and_gives_up(finished):
    state, row = finished
    state["fail"] = workable.KeyRejected()
    report(row)

    assert len(state["broken"]) == 1
    assert state["reported"] == []
