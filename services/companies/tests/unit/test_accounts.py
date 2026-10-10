import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from app.constants.audit import AUDIT_RETENTION_DAYS
from app.constants.invites import InviteStatus
from app.constants.roles import Role
from app.integrations import billing, rounds
from app.models.companies import Company, Member
from app.services import accounts as account_service
from app.services import company_deletion, retention
from app.storage import accounts, audit, processed_events

INTERVIEW_ID = uuid.uuid4()


def membership(role, owners):
    company = Company(id=uuid.uuid4(), name="Acme")
    member = Member(id=uuid.uuid4(), company_id=company.id, user_id="ann", role=role)

    return member, company, owners


@pytest.fixture
def calls(monkeypatch):
    done = []

    async def delete_company(company_id):
        done.append(("company", company_id))

    async def remove_member(member_id):
        done.append(("member", member_id))

    async def forget(user_id, email):
        done.append(("candidate", user_id, email))

    monkeypatch.setattr(company_deletion, "delete_company", delete_company)
    monkeypatch.setattr(accounts, "remove_member", remove_member)
    monkeypatch.setattr(accounts, "forget_candidate", forget)

    async def forget_decisions(user_id):
        done.append(("audit", user_id))

    monkeypatch.setattr(audit, "forget_user", forget_decisions)

    return done


def test_a_company_goes_with_its_only_owner_other_memberships_just_end(calls, monkeypatch):
    sole = membership(Role.OWNER, owners=1)
    shared = membership(Role.OWNER, owners=2)
    admin = membership(Role.ADMIN, owners=1)

    async def memberships(user_id):
        return [sole, shared, admin]

    monkeypatch.setattr(accounts, "memberships", memberships)

    asyncio.run(account_service.delete_user("ann", "ann@example.com"))

    assert calls == [
        ("company", sole[1].id),
        ("member", shared[0].id),
        ("member", admin[0].id),
        ("candidate", "ann", "ann@example.com"),
        ("audit", "ann"),
    ]


def test_retention_deletes_results_and_holds_before_the_invites_in_batches(monkeypatch):
    done = []
    expired = uuid.uuid4()
    batches = [
        [
            (
                expired,
                INTERVIEW_ID,
                "ann@example.com",
                InviteStatus.IN_PROCESS,
                f"{INTERVIEW_ID}:ann-key",
            )
        ],
        [],
    ]

    async def expired_invites(before, limit):
        return batches.pop(0)

    async def release(key):
        done.append(("billing", key))

    async def delete_sessions(invite_ids):
        done.append(("rounds", invite_ids))

    async def delete_invites(invite_ids):
        done.append(("invites", invite_ids))

    monkeypatch.setattr(accounts, "expired_invites", expired_invites)
    monkeypatch.setattr(rounds, "delete_invite_sessions", delete_sessions)
    monkeypatch.setattr(accounts, "delete_invites", delete_invites)
    monkeypatch.setattr(billing, "release_candidate", release)

    assert asyncio.run(retention.delete_expired_candidates()) == 1
    # A candidate stuck in process gives their credits back as they go.
    assert done == [
        ("rounds", [expired]),
        ("billing", f"{INTERVIEW_ID}:ann-key"),
        ("invites", [expired]),
    ]


def test_retention_keeps_the_invites_when_rounds_fails(monkeypatch):
    deleted = []

    async def expired_invites(before, limit):
        return [(uuid.uuid4(), INTERVIEW_ID, "ann@example.com", InviteStatus.INVITED)]

    async def rounds_down(invite_ids):
        raise httpx.ConnectError("rounds is down")

    async def delete_invites(invite_ids):
        deleted.append(invite_ids)

    monkeypatch.setattr(accounts, "expired_invites", expired_invites)
    monkeypatch.setattr(rounds, "delete_invite_sessions", rounds_down)
    monkeypatch.setattr(accounts, "delete_invites", delete_invites)

    with pytest.raises(httpx.ConnectError):
        asyncio.run(retention.delete_expired_candidates())

    assert deleted == []


def test_cloud_scheduler_runs_retention_through_its_route(client, monkeypatch):
    async def expired_invites(before, limit):
        return []

    cutoffs = []

    async def delete_before(before):
        cutoffs.append(before)

        return 0

    async def forget(before):
        cutoffs.append(before)

        return 0

    monkeypatch.setattr(accounts, "expired_invites", expired_invites)
    monkeypatch.setattr(audit, "delete_before", delete_before)
    monkeypatch.setattr(processed_events, "forget", forget)

    assert client.post("/internal/schedules/retention").status_code == 204
    # Audit events go after 24 months; the notes of processed events after Pub/Sub's redeliveries.
    assert len(cutoffs) == 2
    assert datetime.now(UTC) - cutoffs[0] > timedelta(days=AUDIT_RETENTION_DAYS - 1)
    assert timedelta(days=7) < datetime.now(UTC) - cutoffs[1] < timedelta(days=9)
