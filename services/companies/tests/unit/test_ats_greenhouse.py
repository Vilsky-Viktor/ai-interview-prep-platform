import asyncio
import hashlib
import hmac
import json
import uuid

import pytest
from fastapi import HTTPException

from app.integrations import greenhouse
from app.integrations.errors import KeyRejected
from app.models.ats import AtsCandidate, AtsConnection, AtsJobLink
from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services import ats as integrations
from app.services import ats_candidates as flow
from app.services import candidate_invites
from app.storage import ats, ats_candidates, companies, interviews, invites

SECRET = "webhook-secret"
# The real write-back: the shared conftest replaces it for every other test.
REAL_REPORT = flow.report
CONNECTION_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()


def sign(body: bytes) -> str:
    return "sha256 " + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


def event(email="ann@example.com", job=101, stage=None, action="candidate_stage_change") -> bytes:
    stage = stage or {"id": 7, "name": "Assessment"}
    application = {
        "id": 55,
        "candidate": {"id": 44, "email_addresses": [{"value": email}]},
        "current_stage": stage,
        "jobs": [{"id": job}],
    }

    return json.dumps({"action": action, "payload": {"application": application}}).encode()


@pytest.fixture
def world(monkeypatch):
    """A Greenhouse connection with job 101 linked at stage `state["stage"]`, the candidate rows
    in memory, and invites recorded instead of sent."""
    connection = AtsConnection(
        id=CONNECTION_ID,
        company_id=uuid.uuid4(),
        provider="greenhouse",
        status="connected",
        created_by="ann",
    )
    interview = Interview(id=INTERVIEW_ID, company_id=connection.company_id, set_id=uuid.uuid4())
    state = {"connection": connection, "stage": "7", "rows": {}, "sent": []}

    async def connection_by_id(connection_id):
        return state["connection"] if connection_id == CONNECTION_ID else None

    async def link_for_job(connection_id, job_id):
        if job_id != "101":
            return None

        return AtsJobLink(
            id=uuid.uuid4(),
            connection_id=connection_id,
            interview_id=INTERVIEW_ID,
            job_id=job_id,
            stage_id=state["stage"],
        )

    async def key(found):
        return {"client_id": "id", "client_secret": "secret", "webhook_secret": SECRET}

    async def add(connection_id, link_id, interview_id, candidate_id, email):
        return state["rows"].setdefault(
            candidate_id,
            AtsCandidate(
                id=uuid.uuid4(), interview_id=interview_id, candidate_id=candidate_id, email=email
            ),
        )

    async def claim(row_id, statuses):
        return True

    async def get_interview(interview_id):
        return interview

    async def get_company(company_id):
        return Company(id=company_id, name="Acme")

    async def invite(found_interview, company, user, email):
        state["sent"].append((email, user.uid))

        return CandidateInvite(id=uuid.uuid4())

    async def nothing(*args, **kwargs):
        return None

    monkeypatch.setattr(ats, "connection_by_id", connection_by_id)
    monkeypatch.setattr(ats, "link_for_job", link_for_job)
    monkeypatch.setattr(integrations, "credentials", key)
    monkeypatch.setattr(ats_candidates, "add", add)
    monkeypatch.setattr(ats_candidates, "claim", claim)
    monkeypatch.setattr(ats_candidates, "settle", nothing)
    monkeypatch.setattr(interviews, "get", get_interview)
    monkeypatch.setattr(companies, "get", get_company)
    monkeypatch.setattr(candidate_invites, "invite", invite)
    monkeypatch.setattr(flow, "refuse_if_paused", nothing)
    monkeypatch.setattr(flow.outbox_service, "flush_quietly", nothing)

    return state


def receive(body, signature=None, connection_id=CONNECTION_ID):
    signature = sign(body) if signature is None else signature
    asyncio.run(flow.receive_greenhouse(connection_id, body, signature))


def test_a_candidate_moved_into_the_linked_stage_is_invited(world):
    receive(event())

    assert world["sent"] == [("ann@example.com", "ann")]
    # Kept as "<candidate>:<application>", for the note on the application later.
    assert list(world["rows"]) == ["44:55"]


def test_the_linked_stage_matches_by_name_too(world):
    world["stage"] = "Assessment"
    receive(event(stage={"id": 999, "name": "Assessment"}))

    assert world["sent"] == [("ann@example.com", "ann")]


def test_an_unsigned_event_is_refused_and_invites_nobody(world):
    with pytest.raises(HTTPException) as refused:
        receive(event(), signature="sha256 forged")

    assert refused.value.status_code == 401
    assert world["sent"] == []


def test_a_ping_another_stage_or_job_or_a_candidate_without_email_is_ignored(world):
    receive(b'{"action": "ping"}')
    receive(event(action="new_candidate_application"))
    receive(event(stage={"id": 8, "name": "Offer"}))
    receive(event(job=202))
    receive(event(email=None))

    assert world["sent"] == [] and world["rows"] == {}


def test_an_unknown_or_non_greenhouse_connection_is_ignored_even_unsigned(world):
    receive(event(), signature="", connection_id=uuid.uuid4())
    world["connection"].provider = "workable"
    receive(event(), signature="")
    world["connection"].provider = "greenhouse"
    world["connection"].status = "broken"
    receive(event(), signature="")

    assert world["sent"] == []


@pytest.fixture
def finished(monkeypatch):
    """A candidate Greenhouse sent who finished with 82%, from a connection with no member, and
    notes recorded instead of sent."""
    monkeypatch.setattr(flow, "report", REAL_REPORT)
    connection = AtsConnection(id=uuid.uuid4(), provider="greenhouse", status="connected")
    row = AtsCandidate(id=uuid.uuid4(), candidate_id="44:55", invite_id=uuid.uuid4())
    sent = CandidateInvite(id=row.invite_id, grade=82, flagged=False)
    interview = Interview(
        id=INTERVIEW_ID, company_id=uuid.uuid4(), title="Accountant", pass_mark=70
    )
    state = {"notes": [], "reported": [], "broken": [], "fail": None}

    async def for_invite(invite_id):
        return row, connection

    async def key(found):
        return {"client_id": "id", "client_secret": "secret", "webhook_secret": SECRET}

    async def comment(client_id, client_secret, candidate_id, member, text, **rest):
        if state["fail"]:
            raise state["fail"]

        state["notes"].append((client_id, candidate_id, member, text))

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
    monkeypatch.setattr(greenhouse, "comment", comment)
    monkeypatch.setattr(invites, "get", get_invite)
    monkeypatch.setattr(interviews, "get", get_interview)

    return state, row


def report(row):
    data = {"candidate_invite_id": str(row.invite_id), "answered": 3}
    asyncio.run(flow.report("interview.finished", data))


def test_results_go_back_to_greenhouse_as_a_note_without_a_member(finished):
    state, row = finished
    report(row)

    [(client_id, candidate_id, member, text)] = state["notes"]
    assert (client_id, candidate_id, member) == ("id", "44:55", None)
    assert "Grade: 82% (passed)" in text
    assert state["reported"] == [row.id]


def test_a_key_greenhouse_refuses_marks_the_connection_broken_and_gives_up(finished):
    state, row = finished
    state["fail"] = KeyRejected()
    report(row)

    assert len(state["broken"]) == 1
    assert state["reported"] == []
