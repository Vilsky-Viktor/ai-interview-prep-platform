import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest
from prepza_common.notifications import notification

from app.constants.invites import INVITE_EXPIRY_DAYS, InviteStatus
from app.integrations import billing, rounds
from app.services import candidate_billing
from app.services import outbox as outbox_service
from app.storage import interviews, invites

INTERVIEW_ID = uuid.uuid4()


@pytest.fixture
def ledger(monkeypatch):
    calls = []

    async def charge(key):
        calls.append(("charge", key))

    async def release(key):
        calls.append(("release", key))

    monkeypatch.setattr(billing, "charge_candidate", charge)
    monkeypatch.setattr(billing, "release_candidate", release)

    return calls


COMPANY_ID = uuid.uuid4()


def finished(monkeypatch, status=InviteStatus.IN_PROCESS):
    """The invite, and the notifications saved as it's finished."""
    invite = SimpleNamespace(
        id=uuid.uuid4(), interview_id=INTERVIEW_ID, email="carol@example.com", status=status
    )
    notices = []

    async def fake_get(invite_id):
        return invite

    async def fake_finish(invite_id, notice):
        notices.append(notice)

    async def fake_interview(interview_id):
        return SimpleNamespace(id=interview_id, company_id=COMPANY_ID, title="Backend")

    async def fake_scores(invite_ids):
        return {str(invite.id): {"progress": 100, "grade": 85, "finished": True}}

    async def no_flush():
        pass

    monkeypatch.setattr(invites, "get", fake_get)
    monkeypatch.setattr(invites, "finish", fake_finish)
    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(rounds, "invite_scores", fake_scores)
    monkeypatch.setattr(outbox_service, "flush_quietly", no_flush)

    return invite, notices


def test_a_finished_interview_with_an_answer_charges_and_tells_the_company(ledger, monkeypatch):
    invite, notices = finished(monkeypatch)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 2}
        )
    )

    assert notices == [
        notification(
            "company",
            COMPANY_ID,
            "candidate_finished",
            f"/company/{COMPANY_ID}/interviews/{INTERVIEW_ID}",
            # One per invite, however often the event comes.
            key=str(invite.id),
            email="carol@example.com",
            title="Backend",
            grade=85,
        )
    ]
    assert ledger == [("charge", f"{INTERVIEW_ID}:carol@example.com")]


def test_rounds_being_down_doesnt_hold_up_the_charge(ledger, monkeypatch):
    invite, notices = finished(monkeypatch)

    async def down(invite_ids):
        raise httpx.ConnectError("rounds is down")

    monkeypatch.setattr(rounds, "invite_scores", down)
    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 2}
        )
    )

    assert "grade" not in notices[0]["data"]
    assert ledger == [("charge", f"{INTERVIEW_ID}:carol@example.com")]


def test_a_finished_interview_without_an_answer_gives_the_credits_back(ledger, monkeypatch):
    invite, notices = finished(monkeypatch)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 0}
        )
    )

    # Finished, but nobody is told.
    assert notices == [None]
    assert ledger == [("release", f"{INTERVIEW_ID}:carol@example.com")]


def test_a_deleted_candidate_is_left_alone(ledger, monkeypatch):
    invite, notices = finished(monkeypatch, InviteStatus.DELETED)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 3}
        )
    )

    assert (notices, ledger) == ([], [])


def test_invites_never_started_expire_and_give_their_credits_back(ledger, monkeypatch):
    stale = SimpleNamespace(interview_id=INTERVIEW_ID, email="dave@example.com")
    asked = []

    async def fake_expire(before):
        asked.append(before)

        return [stale]

    monkeypatch.setattr(invites, "expire_unstarted", fake_expire)

    assert asyncio.run(candidate_billing.expire_unstarted()) == 1
    expected = datetime.now(UTC) - timedelta(days=INVITE_EXPIRY_DAYS)
    assert abs((asked[0] - expected).total_seconds()) < 5
    assert ledger == [("release", f"{INTERVIEW_ID}:dave@example.com")]


def test_a_leaving_candidate_frees_only_unfinished_invites(ledger):
    asyncio.run(
        candidate_billing.release_unfinished(
            [
                (INTERVIEW_ID, "a@example.com", InviteStatus.INVITED),
                (INTERVIEW_ID, "b@example.com", InviteStatus.IN_PROCESS),
                (INTERVIEW_ID, "c@example.com", InviteStatus.FINISHED),
            ]
        )
    )

    assert ledger == [
        ("release", f"{INTERVIEW_ID}:a@example.com"),
        ("release", f"{INTERVIEW_ID}:b@example.com"),
    ]
