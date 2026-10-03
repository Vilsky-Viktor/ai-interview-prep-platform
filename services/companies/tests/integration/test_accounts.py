import uuid
from datetime import UTC, datetime, timedelta

from app.constants.invites import InviteStatus
from app.storage import accounts, companies, interviews, invites


def test_a_deleted_candidate_keeps_a_row_without_their_email(run):
    async def scenario():
        company = await companies.create("Acme", "owner", "owner@example.com")
        interview = await interviews.create(company.id, uuid.uuid4(), "en")
        first = await invites.upsert(interview.id, "gone@example.com", "Backend", "Acme", "en")
        await invites.start(first, "gone")
        # A second address of the same person, never started: matched by email.
        await invites.upsert(interview.id, "Gone2@Example.com", "Backend", "Acme", "en")
        await accounts.forget_candidate("gone", "gone2@example.com")

        return (
            await invites.list_for_interview(interview.id, 0, 10),
            await invites.get_by_token(first.token),
        )

    rows, by_old_token = run(scenario())

    assert {row.status for row in rows} == {InviteStatus.DELETED}
    assert all(row.email.startswith("deleted-") and row.user_id is None for row in rows)
    assert by_old_token is None


def test_memberships_report_how_many_owners_each_company_has(run):
    async def scenario():
        alone = await companies.create("Alone Inc", "ann", "ann@example.com")
        found = await accounts.memberships("ann")

        return alone.id, found

    company_id, found = run(scenario())

    assert [(company.id, owners) for _, company, owners in found] == [(company_id, 1)]


def test_only_invites_older_than_the_cutoff_expire(run):
    async def scenario():
        company = await companies.create("Acme", "owner", "owner@example.com")
        interview = await interviews.create(company.id, uuid.uuid4(), "en")
        invite = await invites.upsert(interview.id, "carol@example.com", "Backend", "Acme", "en")
        recent = await accounts.expired_invites(datetime.now(UTC) - timedelta(days=365))
        everything = await accounts.expired_invites(datetime.now(UTC) + timedelta(seconds=1))
        await accounts.delete_invites([invite.id])

        return invite.id, recent, everything, await invites.get_by_token(invite.token)

    invite_id, recent, everything, after = run(scenario())

    assert invite_id not in recent
    assert invite_id in everything
    assert after is None
