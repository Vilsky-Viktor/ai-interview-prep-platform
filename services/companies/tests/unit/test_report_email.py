import base64
import uuid
from datetime import UTC, datetime

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.config.settings import settings
from app.constants.reports import NO_FINISHED_CANDIDATES, TOO_MANY_REPORT_EMAILS
from app.integrations import rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.services import outbox as outbox_service
from app.services import report_emails
from app.storage import companies, interviews, reports
from tests.unit import fake_candidates
from tests.unit.fake_redis import FakeRedis

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
INVITE_ID = uuid.uuid4()
URL = f"/interviews/{INTERVIEW_ID}/candidates/{INVITE_ID}/report/email"
PDF = base64.b64encode(b"%PDF-1.3 a report").decode()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def queued(monkeypatch):
    """A member's candidate; returns the events queued for notifications."""
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )
    invite = CandidateInvite(
        id=INVITE_ID,
        interview_id=INTERVIEW_ID,
        email="ann@example.com",
        token="token-ann",
        status="finished",
        created_at=datetime.now(UTC),
    )
    interview = Interview(
        pass_mark=70,
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        set_id=uuid.uuid4(),
        title="Backend",
        language="en",
    )
    fake_candidates.add(invite)
    company = Company(id=COMPANY_ID, name="Arcolabs", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role="member")
    ]
    events = []

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_queue(data):
        events.append(data)

    async def no_flush():
        return None

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(reports, "queue_email", fake_queue)
    redis = FakeRedis()
    monkeypatch.setattr(report_emails, "get_redis", lambda: redis)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)

    return events


def test_a_member_emails_the_pdf_report_and_replies_go_to_them(client, queued):
    response = client.post(URL, json={"email": "Boss@Example.com", "pdf": PDF})

    assert response.status_code == 202
    [event] = queued
    assert (event["email"], event["sender"], event["reply_to"]) == (
        "boss@example.com",
        "Bob",
        "bob@example.com",
    )
    assert (event["candidate"], event["company"], event["title"]) == (
        "ann@example.com",
        "Arcolabs",
        "Backend",
    )
    assert event["pdf"] == PDF


def test_only_a_pdf_is_emailed(client, queued):
    not_pdf = base64.b64encode(b"<html>hello</html>").decode()

    assert client.post(URL, json={"email": "boss@example.com", "pdf": not_pdf}).status_code == 422
    assert client.post(URL, json={"email": "boss@example.com", "pdf": "%%%"}).status_code == 422
    assert queued == []


def test_the_tests_report_lists_candidates_as_storage_orders_them(client, queued, monkeypatch):
    def invite(email, status):
        return CandidateInvite(
            id=uuid.uuid4(),
            interview_id=INTERVIEW_ID,
            email=email,
            token=f"t-{email}",
            status=status,
            created_at=datetime.now(UTC),
        )

    # Best grade first, deleted ones left out: storage's order (see the integration tests).
    everyone = [invite("top@example.com", "finished"), invite("low@example.com", "finished")]
    fake_candidates.ROWS[:] = everyone
    grades = {"low@example.com": 40, "top@example.com": 90}

    async def fake_scores(invite_ids):
        return {
            str(row.id): {"progress": 100, "grade": grades[row.email], "finished": True}
            for row in everyone
            if row.id in invite_ids
        }

    monkeypatch.setattr(rounds, "invite_scores", fake_scores)

    report = client.get(f"/interviews/{INTERVIEW_ID}/report").json()

    assert (report["company"], report["pass_mark"]) == ("Arcolabs", 70)
    assert [(row["email"], row["passed"]) for row in report["candidates"]] == [
        ("top@example.com", True),
        ("low@example.com", False),
    ]


def test_the_tests_report_is_emailed_as_a_candidates_report(client, queued):
    response = client.post(
        f"/interviews/{INTERVIEW_ID}/report/email", json={"email": "boss@example.com", "pdf": PDF}
    )

    assert response.status_code == 202
    [event] = queued
    assert (event["kind"], event["title"], event["filename"]) == (
        "candidates",
        "Backend",
        "Candidates Backend.pdf",
    )
    assert "candidate" not in event


def test_no_report_is_emailed_before_a_candidate_finishes(client, queued, monkeypatch):
    unfinished = CandidateInvite(
        id=INVITE_ID,
        interview_id=INTERVIEW_ID,
        email="ann@example.com",
        token="token-ann",
        status="in_process",
        created_at=datetime.now(UTC),
    )
    interview = Interview(id=INTERVIEW_ID, company_id=COMPANY_ID, title="Backend", language="en")
    fake_candidates.ROWS[:] = [unfinished]

    async def fake_interview(_interview_id):
        return interview

    monkeypatch.setattr(interviews, "get", fake_interview)
    body = {"email": "boss@example.com", "pdf": PDF}

    refused = client.post(URL, json=body)
    refused_all = client.post(f"/interviews/{INTERVIEW_ID}/report/email", json=body)

    assert (refused.status_code, refused_all.status_code) == (409, 409)
    assert refused.json()["detail"] == NO_FINISHED_CANDIDATES
    assert queued == []


def test_a_company_emails_a_limited_number_of_reports_a_day(client, queued, monkeypatch):
    monkeypatch.setattr(settings, "report_emails_per_company_day", 2)

    def send(number):
        return client.post(URL, json={"email": f"boss{number}@example.com", "pdf": PDF})

    assert [send(number).status_code for number in range(2)] == [202, 202]

    refused = send(2)

    assert refused.status_code == 429
    assert refused.json()["detail"] == TOO_MANY_REPORT_EMAILS
    assert len(queued) == 2
