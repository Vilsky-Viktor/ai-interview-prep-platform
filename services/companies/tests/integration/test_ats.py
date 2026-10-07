import uuid

from app.constants.ats import AtsProvider
from app.storage import ats, companies, interviews

JOB = {"id": "A1", "name": "Accountant"}
STAGE = {"id": "assessment", "name": "Assessment"}


def test_a_reconnect_keeps_linked_jobs_and_a_disconnect_removes_them(run):
    async def scenario():
        company = await companies.create(f"ATS {uuid.uuid4()}", "ann", "ann@example.com")
        interview = await interviews.create(company.id, uuid.uuid4(), "en")
        await ats.connect(company.id, AtsProvider.WORKABLE, "acme", "sealed-1", "ann")
        connection = await ats.connection(company.id, AtsProvider.WORKABLE)
        first = await ats.add_link(connection.id, interview.id, JOB, STAGE)
        # The same job twice is refused; one job has one interview.
        again = await ats.add_link(connection.id, interview.id, JOB, STAGE)
        await ats.mark_broken(connection.id)
        await ats.connect(company.id, AtsProvider.WORKABLE, "acme", "sealed-2", "bob")
        reconnected = await ats.connection(company.id, AtsProvider.WORKABLE)
        kept = await ats.links(company.id)
        await ats.disconnect(company.id, AtsProvider.WORKABLE)
        gone = await ats.links(company.id), await ats.connections(company.id)
        await companies.delete(company.id)

        return connection, first, again, reconnected, kept, gone

    connection, first, again, reconnected, kept, gone = run(scenario())

    assert (first, again) == (True, False)
    # A reconnect replaces the key and who connected, and works again, with the same row.
    assert reconnected.id == connection.id
    assert (reconnected.credentials, reconnected.created_by, reconnected.status) == (
        "sealed-2",
        "bob",
        "connected",
    )
    assert [(link.job_name, link.stage_name, provider) for link, provider, _ in kept] == [
        ("Accountant", "Assessment", "workable")
    ]
    assert gone == ([], [])


def test_a_company_only_unlinks_its_own_jobs(run):
    async def scenario():
        mine = await companies.create(f"ATS mine {uuid.uuid4()}", "ann", "ann@example.com")
        theirs = await companies.create(f"ATS theirs {uuid.uuid4()}", "eve", "eve@example.com")
        interview = await interviews.create(mine.id, uuid.uuid4(), "en")
        await ats.connect(mine.id, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        connection = await ats.connection(mine.id, AtsProvider.WORKABLE)
        await ats.add_link(connection.id, interview.id, JOB, STAGE)
        [(link, _, _)] = await ats.links(mine.id)
        by_them = await ats.remove_link(theirs.id, link.id)
        by_me = await ats.remove_link(mine.id, link.id)
        left = await ats.links(mine.id)
        await companies.delete(mine.id)
        await companies.delete(theirs.id)

        return by_them, by_me, left

    by_them, by_me, left = run(scenario())

    assert (by_them, by_me, left) == (False, True, [])
