import uuid

from app.constants.invites import InviteStatus
from app.helpers.notifications import invite_undelivered
from app.storage import companies, interviews, invites


async def interview():
    company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")

    return await interviews.create(company.id, uuid.uuid4(), "en")


def test_inviting_the_same_address_again_returns_the_same_invite(run):
    async def scenario():
        found = await interview()
        first = await invites.upsert(found.id, "Carol@Example.com", "Backend", "Acme", "en")
        again = await invites.upsert(found.id, "carol@example.com", "Backend", "Acme", "en")

        return first, again

    first, again = run(scenario())

    assert (first.id, first.token) == (again.id, again.token)
    assert first.email == "carol@example.com"
    assert first.status == InviteStatus.INVITED


def test_an_undelivered_invite_is_marked_until_it_is_sent_again(run):
    async def scenario():
        found = await interview()
        invite = await invites.upsert(found.id, "erin@example.com", "Backend", "Acme", "en")
        await invites.mark_undelivered(invite.id, invite_undelivered(found, invite.email))
        bounced, _ = await invites.get_by_token(invite.token)
        await invites.upsert(found.id, "erin@example.com", "Backend", "Acme", "en")
        resent, _ = await invites.get_by_token(invite.token)

        return bounced, resent

    bounced, resent = run(scenario())

    assert bounced.status == InviteStatus.UNDELIVERED
    assert resent.status == InviteStatus.INVITED


def test_a_started_invite_is_never_marked_undelivered(run):
    async def scenario():
        found = await interview()
        invite = await invites.upsert(found.id, "fay@example.com", "Backend", "Acme", "en")
        await invites.start(invite, "fay-uid")
        await invites.mark_undelivered(invite.id, invite_undelivered(found, invite.email))
        stored, _ = await invites.get_by_token(invite.token)

        return stored

    assert run(scenario()).status == InviteStatus.IN_PROCESS


def test_an_invite_moves_from_invited_to_in_process_to_finished(run):
    async def scenario():
        found = await interview()
        invite = await invites.upsert(found.id, "dave@example.com", "Backend", "Acme", "en")
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


def test_only_interviews_without_a_candidate_count_as_waiting(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        first = await interviews.create(company.id, uuid.uuid4(), "en")
        await interviews.create(company.id, uuid.uuid4(), "en")
        before = await interviews.without_candidates(company.id)
        invite = await invites.upsert(first.id, "dan@example.com", "Backend", "Acme", "en")
        invited = await interviews.without_candidates(company.id)
        await invites.remove(invite.id)
        revoked = await interviews.without_candidates(company.id)

        return before, invited, revoked

    # Two waiting; an invite takes one out; revoking the invite puts it back.
    assert run(scenario()) == (2, 1, 2)
