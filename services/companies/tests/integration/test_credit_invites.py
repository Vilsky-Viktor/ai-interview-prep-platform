import uuid

from sqlalchemy import update

from app.constants.invites import InviteStatus
from app.models.invites import CandidateInvite
from app.storage import companies, credit_invites, interviews, invites
from app.storage.db import Session


async def interview_of(company, title: str):
    found = await interviews.create(company.id, uuid.uuid4(), "en")
    await interviews.set_title(found.id, title)

    return found


async def invite(found, email, status=InviteStatus.INVITED, hold_key=None):
    """An invite in this status; without a hold key, like invites made before they had one."""
    created, _ = await invites.upsert(found.id, email, "", "Acme", "en", hold_key=hold_key)

    async with Session() as session:
        await session.execute(
            update(CandidateInvite).where(CandidateInvite.id == created.id).values(status=status)
        )
        await session.commit()

    return created


def test_only_open_invites_hold_credits_newest_first(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        other = await companies.create(f"Other {uuid.uuid4()}", "owner", "owner@example.com")
        backend = await interview_of(company, "Backend")
        frontend = await interview_of(company, "Frontend")
        # Invited in this order, so newest first is cleo, ben, ann.
        await invite(backend, "ann@example.com", hold_key="h-ann")
        await invite(frontend, "ben@example.com", InviteStatus.UNDELIVERED, "h-ben")
        await invite(frontend, "cleo@example.com", InviteStatus.IN_PROCESS, "h-cleo")
        # Charged, given back, or gone: nothing held.
        await invite(backend, "dan@example.com", InviteStatus.FINISHED, "h-dan")
        await invite(backend, "eve@example.com", InviteStatus.EXPIRED, "h-eve")
        await invite(backend, "fay@example.com", InviteStatus.DELETED, "h-fay")
        # Another company's candidate.
        await invite(await interview_of(other, "Elsewhere"), "gus@example.com")

        return (
            await credit_invites.count_holding(company.id),
            await credit_invites.holding(company.id, 0, 2),
            await credit_invites.holding(company.id, 2, 2),
        )

    count, first, second = run(scenario())

    assert count == 3
    assert [(row.email, interview.title) for row, interview in first + second] == [
        ("cleo@example.com", "Frontend"),
        ("ben@example.com", "Frontend"),
        ("ann@example.com", "Backend"),
    ]


def test_history_keys_find_the_companys_invites_also_by_the_older_key(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        other = await companies.create(f"Other {uuid.uuid4()}", "owner", "owner@example.com")
        backend = await interview_of(company, "Backend")
        elsewhere = await interview_of(other, "Elsewhere")
        await invite(backend, "ann@example.com", InviteStatus.FINISHED, "h-ann")
        # Made before invites had their own key: found by "{interview_id}:{email}".
        await invite(backend, "Ben@Example.com", InviteStatus.FINISHED)
        await invite(backend, "cid@example.com", InviteStatus.DELETED, "h-cid")
        await invite(elsewhere, "dan@example.com", InviteStatus.FINISHED, "h-dan")
        legacy = f"{backend.id}:ben@example.com"
        keys = ["h-ann", legacy, "h-cid", "h-dan", "h-unknown"]

        return legacy, await credit_invites.by_hold_keys(company.id, keys)

    legacy, found = run(scenario())

    assert {key: (row.email, interview.title) for key, (row, interview) in found.items()} == {
        "h-ann": ("ann@example.com", "Backend"),
        legacy: ("ben@example.com", "Backend"),
    }


def test_no_keys_ask_nothing(run):
    assert run(credit_invites.by_hold_keys(uuid.uuid4(), [])) == {}
