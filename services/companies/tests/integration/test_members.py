import uuid

from app.constants.roles import EDITORS
from app.storage import companies, members


def test_an_accepted_invite_link_stops_working_and_a_removed_admin_is_gone(run):
    async def scenario():
        company = await companies.create(f"Members {uuid.uuid4()}", "ann", "ann@example.com")
        bob = await members.add(company.id, "bob@example.com", "admin")
        cid = await members.add(company.id, "cid@example.com", "admin")
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


def test_a_viewer_keeps_their_role_on_joining_and_the_owner_changes_it(run):
    uid = f"bob-{uuid.uuid4()}"

    async def scenario():
        company = await companies.create(f"Viewers {uuid.uuid4()}", "ann", "ann@example.com")
        bob = await members.add(company.id, "bob@example.com", "viewer")
        # An id of its own: other tests' companies have a "bob" too.
        await members.accept(bob, uid)
        joined = await members.list_for_company(company.id, 0, 10)
        top_up_before = await companies.list_for_user(uid, 0, 10, EDITORS)
        await members.set_role(bob.id, "admin")
        changed = await members.list_for_company(company.id, 0, 10)
        top_up_after = await companies.list_for_user(uid, 0, 10, EDITORS)
        await companies.delete(company.id)

        return joined, changed, top_up_before, [item.id for item in top_up_after], company.id

    joined, changed, top_up_before, top_up_after, company_id = run(scenario())

    assert [(row.user_id, row.role) for row in joined] == [("ann", "owner"), (uid, "viewer")]
    assert [(row.user_id, row.role) for row in changed] == [("ann", "owner"), (uid, "admin")]
    # Only an owner or admin tops the company up.
    assert top_up_before == []
    assert top_up_after == [company_id]
