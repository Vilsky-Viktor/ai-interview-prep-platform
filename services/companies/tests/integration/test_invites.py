import uuid

from app.constants.invites import InviteStatus
from app.storage import companies, interviews, invites


async def interview():
    company = await companies.create("Acme", "owner", "owner@example.com")

    return await interviews.create(company.id, uuid.uuid4(), False)


def test_inviting_the_same_address_again_returns_the_same_invite(run):
    async def scenario():
        found = await interview()
        first = await invites.upsert(found.id, "Carol@Example.com")
        again = await invites.upsert(found.id, "carol@example.com")

        return first, again

    first, again = run(scenario())

    assert (first.id, first.token) == (again.id, again.token)
    assert first.email == "carol@example.com"
    assert first.status == InviteStatus.INVITED


def test_an_invite_moves_from_invited_to_in_process_to_finished(run):
    async def scenario():
        found = await interview()
        invite = await invites.upsert(found.id, "dave@example.com")
        await invites.start(invite, "dave-uid")
        started, _ = await invites.get_by_token(invite.token)
        await invites.set_status([invite.id], InviteStatus.FINISHED)
        # Starting again, e.g. reopening the link, never reopens a finished interview.
        await invites.start(invite, "dave-uid")
        finished, _ = await invites.get_by_token(invite.token)

        return started, finished

    started, finished = run(scenario())

    assert (started.status, started.user_id) == (InviteStatus.IN_PROCESS, "dave-uid")
    assert finished.status == InviteStatus.FINISHED
