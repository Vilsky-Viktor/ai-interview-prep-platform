import uuid

from prepza_common.constants import LEGAL_VERSIONS

from app.models.companies import Member
from app.storage import companies, email_reminders
from app.storage.db import Session


def test_company_names_are_unique_ignoring_case_until_deleted(run):
    async def scenario():
        first = await companies.create("Unique Co", "ann", "ann@example.com")
        taken = await companies.create("unique co", "bob", "bob@example.com")
        await companies.delete(first.id)
        freed = await companies.create("UNIQUE CO", "bob", "bob@example.com")

        return first, taken, freed

    first, taken, freed = run(scenario())

    assert first is not None
    assert taken is None
    assert freed is not None and freed.name == "UNIQUE CO"


def test_a_new_company_keeps_the_dpa_version_its_owner_accepted(run):
    async def scenario():
        made = await companies.create(f"DPA {uuid.uuid4()}", "ann", "ann@example.com")
        found = await companies.get(made.id)
        await companies.delete(made.id)

        return found

    assert run(scenario()).dpa_version == LEGAL_VERSIONS["dpa"]


def test_the_dpa_notice_goes_to_joined_owners_and_admins_only(run):
    owner, viewer = f"own-{uuid.uuid4()}", f"view-{uuid.uuid4()}"

    async def scenario():
        made = await companies.create(f"Editors {uuid.uuid4()}", owner, "own@example.com")

        async with Session() as session:
            session.add_all(
                [
                    Member(
                        company_id=made.id, user_id=viewer, invited_email="v@x.io", role="viewer"
                    ),
                    # Invited, not joined yet.
                    Member(company_id=made.id, invited_email="a@x.io", role="admin"),
                ]
            )
            await session.commit()

        found = await email_reminders.editor_ids()
        await companies.delete(made.id)

        return found

    found = run(scenario())

    assert owner in found and viewer not in found
