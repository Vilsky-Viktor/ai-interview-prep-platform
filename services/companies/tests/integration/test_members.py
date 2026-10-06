import uuid

from app.storage import companies, members


def test_an_accepted_invite_link_stops_working_and_a_removed_admin_is_gone(run):
    async def scenario():
        company = await companies.create(f"Members {uuid.uuid4()}", "ann", "ann@example.com")
        bob = await members.add_admin(company.id, "bob@example.com")
        cid = await members.add_admin(company.id, "cid@example.com")
        await members.accept(bob, "bob")
        reused = await members.get_by_token(bob.token)
        await members.remove(cid.id)
        left = await members.list_for_company(company.id, 0, 10)
        await companies.delete(company.id)

        return reused, left

    reused, left = run(scenario())

    assert reused is None
    assert [(row.invited_email, row.user_id, row.token) for row in left] == [
        ("ann@example.com", "ann", None),
        ("bob@example.com", "bob", None),
    ]
