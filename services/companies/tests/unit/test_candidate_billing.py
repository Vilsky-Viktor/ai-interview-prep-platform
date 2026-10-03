import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.constants.invites import INVITE_EXPIRY_DAYS, InviteStatus
from app.integrations import billing
from app.services import candidate_billing
from app.storage import invites

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


def finished(monkeypatch, status=InviteStatus.IN_PROCESS):
    invite = SimpleNamespace(
        id=uuid.uuid4(), interview_id=INTERVIEW_ID, email="carol@example.com", status=status
    )
    statuses = []

    async def fake_get(invite_id):
        return invite

    async def fake_set(ids, value):
        statuses.append(value)

    monkeypatch.setattr(invites, "get", fake_get)
    monkeypatch.setattr(invites, "set_status", fake_set)

    return invite, statuses


def test_a_finished_interview_with_an_answer_charges_the_company(ledger, monkeypatch):
    invite, statuses = finished(monkeypatch)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 2}
        )
    )

    assert statuses == [InviteStatus.FINISHED]
    assert ledger == [("charge", f"{INTERVIEW_ID}:carol@example.com")]


def test_a_finished_interview_without_an_answer_gives_the_credits_back(ledger, monkeypatch):
    invite, _ = finished(monkeypatch)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 0}
        )
    )

    assert ledger == [("release", f"{INTERVIEW_ID}:carol@example.com")]


def test_a_deleted_candidate_is_left_alone(ledger, monkeypatch):
    invite, statuses = finished(monkeypatch, InviteStatus.DELETED)

    asyncio.run(
        candidate_billing.handle(
            "interview.finished", {"candidate_invite_id": str(invite.id), "answered": 3}
        )
    )

    assert (statuses, ledger) == ([], [])


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
