from app.storage import shares
from tests.integration.factories import preparation


def test_an_undelivered_share_is_marked_until_it_is_sent_again(run):
    async def scenario():
        set_id = await preparation(public=False)
        invite = await shares.upsert(set_id, "bob@example.com", "owner", "Backend", "Ann")
        await shares.mark_undelivered(invite.id)
        bounced, _ = await shares.get_by_token(invite.token)
        await shares.upsert(set_id, "bob@example.com", "owner", "Backend", "Ann")
        resent, _ = await shares.get_by_token(invite.token)

        return bounced, resent

    bounced, resent = run(scenario())

    assert bounced.undelivered_at is not None
    assert resent.undelivered_at is None


def test_an_accepted_share_is_never_marked_undelivered(run):
    async def scenario():
        set_id = await preparation(public=False)
        invite = await shares.upsert(set_id, "carol@example.com", "owner", "Backend", "Ann")
        await shares.accept(invite, "carol-uid")
        await shares.mark_undelivered(invite.id)
        stored, _ = await shares.get_by_token(invite.token)

        return stored

    assert run(scenario()).undelivered_at is None
