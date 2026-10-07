import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.constants.ats import AtsProvider
from app.models.ats import AtsCandidate, AtsJobLink
from app.services.events import handle
from app.storage import ats, ats_candidates
from app.storage.db import Session

JOB = {"id": "A1", "name": "Accountant"}
STAGE = {"id": "assessment", "name": "Assessment"}


async def linked(company_id, interview_id, job=JOB):
    """A Workable connection with one job linked to the interview and one candidate sent."""
    await ats.connect(company_id, AtsProvider.WORKABLE, "acme", "sealed", "ann")
    connection = await ats.connection(company_id, AtsProvider.WORKABLE)
    link_id = await ats.add_link(connection.id, interview_id, job, STAGE)
    row = await ats_candidates.add(connection.id, link_id, interview_id, "c-1", "Ann@x.com")

    return connection, link_id, row


async def rows_of(model, column, value) -> list:
    async with Session() as session:
        return list((await session.scalars(select(model).where(column == value))).all())


def test_a_deleted_interview_takes_its_links_and_candidates_even_when_delivered_twice(run):
    async def scenario():
        company, deleted, kept = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        connection, _, _ = await linked(company, deleted)
        await ats.add_link(connection.id, kept, {"id": "B2", "name": "Clerk"}, STAGE)
        event = {"interview_id": str(deleted), "company_id": str(company)}
        await handle("interview.deleted", event)
        await handle("interview.deleted", event)
        found = (
            await rows_of(AtsJobLink, AtsJobLink.connection_id, connection.id),
            await rows_of(AtsCandidate, AtsCandidate.connection_id, connection.id),
            await ats.connections(company),
        )
        await ats.delete_company(company)

        return kept, found

    kept, (links, candidates, connections) = run(scenario())

    assert [link.interview_id for link in links] == [kept]
    assert candidates == []
    assert len(connections) == 1


def test_a_deleted_company_takes_its_connections_links_and_candidates(run):
    async def scenario():
        company, other = uuid.uuid4(), uuid.uuid4()
        connection, _, _ = await linked(company, uuid.uuid4())
        theirs, _, _ = await linked(other, uuid.uuid4())
        await handle("company.deleted", {"company_id": str(company)})
        await handle("company.deleted", {"company_id": str(company)})
        found = (
            await ats.connections(company),
            await rows_of(AtsJobLink, AtsJobLink.connection_id, connection.id),
            await rows_of(AtsCandidate, AtsCandidate.connection_id, connection.id),
            len(await rows_of(AtsCandidate, AtsCandidate.connection_id, theirs.id)),
        )
        await ats.delete_company(other)

        return found

    assert run(scenario()) == ([], [], [], 1)


def test_an_accounts_candidates_are_exported_and_deleted_by_email(run):
    async def scenario():
        company = uuid.uuid4()
        await linked(company, uuid.uuid4())
        exported = await ats_candidates.of_email("ANN@x.com")
        await ats_candidates.delete_email("ann@X.com")
        left = await ats_candidates.of_email("ann@x.com")
        await ats.delete_company(company)

        return exported, left

    exported, left = run(scenario())

    assert [row.email for row in exported] == ["ann@x.com"]
    assert left == []


def test_candidates_past_their_retention_period_go(run):
    async def scenario():
        company = uuid.uuid4()
        _, _, old = await linked(company, uuid.uuid4())
        _, _, new = await linked(company, uuid.uuid4(), {"id": "B2", "name": "Clerk"})

        async with Session() as session:
            await session.execute(
                update(AtsCandidate)
                .where(AtsCandidate.id == old.id)
                .values(created_at=datetime.now(UTC) - timedelta(days=400))
            )
            await session.commit()

        deleted = await ats_candidates.delete_older_than(datetime.now(UTC) - timedelta(days=365))
        left = await rows_of(AtsCandidate, AtsCandidate.interview_id, new.interview_id)
        await ats.delete_company(company)

        return deleted, left

    deleted, left = run(scenario())

    assert deleted == 1
    assert len(left) == 1
