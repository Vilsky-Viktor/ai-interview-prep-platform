import base64
import json
import uuid

import pytest

from app.services import ats_candidates
from app.storage import ats

INTERVIEW_ID = uuid.uuid4()
COMPANY_ID = uuid.uuid4()


def push(client, event_type, data):
    message = {
        "data": base64.b64encode(json.dumps(data).encode()).decode(),
        "attributes": {"type": event_type, "event_id": "e-1"},
        "messageId": "m-1",
    }

    return client.post("/internal/events", json={"message": message, "subscription": "s"})


@pytest.fixture
def calls(monkeypatch):
    """What each event leads to, recorded."""
    seen = []

    def record(name):
        async def fake(*args):
            seen.append((name, *args))

        return fake

    monkeypatch.setattr(ats_candidates, "report", record("report"))
    monkeypatch.setattr(ats_candidates, "invite_waiting", record("invite_waiting"))
    monkeypatch.setattr(ats_candidates, "topped_up", record("topped_up"))
    monkeypatch.setattr(ats, "delete_interview", record("delete_interview"))
    monkeypatch.setattr(ats, "delete_company", record("delete_company"))

    return seen


def test_a_finished_candidate_is_reported(client, calls):
    data = {"candidate_invite_id": str(uuid.uuid4()), "interview_id": str(INTERVIEW_ID)}

    assert push(client, "candidate.finished", data).status_code == 204
    assert calls == [("report", data)]


def test_a_ready_interview_invites_its_waiting_candidates(client, calls):
    push(client, "interview.ready", {"interview_id": str(INTERVIEW_ID)})

    assert calls == [("invite_waiting", INTERVIEW_ID)]


def test_a_deleted_interview_or_company_deletes_its_rows(client, calls):
    push(client, "interview.deleted", {"interview_id": str(INTERVIEW_ID), "company_id": "c"})
    push(client, "company.deleted", {"company_id": str(COMPANY_ID)})

    assert calls == [("delete_interview", INTERVIEW_ID), ("delete_company", COMPANY_ID)]


def test_a_company_that_got_credits_invites_its_candidates_short_of_them(client, calls):
    data = {"owner_type": "company", "owner_id": str(COMPANY_ID)}

    assert push(client, "credits.added", data).status_code == 204
    assert calls == [("topped_up", COMPANY_ID)]


def test_credits_another_kind_of_owner_got_are_ignored(client, calls):
    data = {"owner_type": "user", "owner_id": "ann"}

    assert push(client, "credits.added", data).status_code == 204
    assert calls == []


def test_credits_for_a_malformed_company_are_dropped_not_retried(client, calls):
    data = {"owner_type": "company", "owner_id": "acme"}

    assert push(client, "credits.added", data).status_code == 204
    assert calls == []


def test_other_events_are_ignored(client, calls):
    assert push(client, "interview.finished", {"candidate_invite_id": "x"}).status_code == 204
    assert calls == []


def test_a_failing_handler_answers_an_error_so_pubsub_retries(client, monkeypatch):
    async def failing(data):
        raise RuntimeError("ATS down")

    monkeypatch.setattr(ats_candidates, "report", failing)

    with pytest.raises(RuntimeError):
        push(client, "candidate.finished", {"candidate_invite_id": "x"})
