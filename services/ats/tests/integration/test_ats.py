import uuid

from app.constants.ats import AtsProvider, CandidateStatus
from app.storage import ats, ats_candidates

JOB = {"id": "A1", "name": "Accountant"}
STAGE = {"id": "assessment", "name": "Assessment"}


def test_a_reconnect_keeps_linked_jobs_and_a_disconnect_removes_them(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed-1", "ann")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        first = await ats.add_link(connection.id, interview, JOB, STAGE)
        # The same job twice is refused; one job has one interview.
        again = await ats.add_link(connection.id, interview, JOB, STAGE)
        await ats.mark_broken(connection.id)
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed-2", "bob")
        reconnected = await ats.connection(company, AtsProvider.WORKABLE)
        kept = await ats.links(company)
        await ats.disconnect(company, AtsProvider.WORKABLE)
        gone = await ats.links(company), await ats.connections(company)
        await ats.delete_company(company)

        return connection, first, again, reconnected, kept, gone

    connection, first, again, reconnected, kept, gone = run(scenario())

    assert first is not None and again is None
    # A reconnect replaces the key and who connected, and works again, with the same row.
    assert reconnected.id == connection.id
    assert (reconnected.credentials, reconnected.created_by, reconnected.status) == (
        "sealed-2",
        "bob",
        "connected",
    )
    assert [(link.job_name, link.stage_name, provider) for link, provider in kept] == [
        ("Accountant", "Assessment", "workable")
    ]
    assert gone == ([], [])


def test_a_company_only_unlinks_its_own_jobs(run):
    async def scenario():
        mine = uuid.uuid4()
        theirs = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(mine, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        connection = await ats.connection(mine, AtsProvider.WORKABLE)
        await ats.add_link(connection.id, interview, JOB, STAGE)
        [(link, _)] = await ats.links(mine)
        by_them = await ats.remove_link(theirs, link.id)
        by_me = await ats.remove_link(mine, link.id)
        left = await ats.links(mine)
        await ats.delete_company(mine)
        await ats.delete_company(theirs)

        return by_them, by_me, left

    by_them, by_me, left = run(scenario())

    assert (by_them, by_me, left) == (False, True, [])


def test_a_candidate_is_one_row_claimed_once_counted_and_reported_once(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann", "m-1")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        link_id = await ats.add_link(connection.id, interview, JOB, STAGE)
        first = await ats_candidates.add(connection.id, link_id, interview, "c-1", "A@x.com")
        again = await ats_candidates.add(connection.id, link_id, interview, "c-1", "a@x.com")
        claims = [
            await ats_candidates.claim(first.id, (CandidateStatus.WAITING,)),
            await ats_candidates.claim(first.id, (CandidateStatus.WAITING,)),
        ]
        invite = uuid.uuid4()
        await ats_candidates.settle(first.id, CandidateStatus.INVITED, invite_id=invite)
        other = await ats_candidates.add(connection.id, link_id, interview, "c-2", "b@x.com")
        await ats_candidates.settle(other.id, CandidateStatus.FAILED, "credits")
        counts = await ats_candidates.counts(company)
        failed = await ats_candidates.not_invited(company, link_id)
        to_report = await ats_candidates.for_invite(invite)
        await ats_candidates.mark_reported(first.id)
        reported = await ats_candidates.for_invite(invite)
        await ats.delete_company(company)

        return first, again, claims, counts[link_id], failed, to_report, reported

    first, again, claims, counts, failed, to_report, reported = run(scenario())

    assert again.id == first.id and first.email == "a@x.com"
    assert claims == [True, False]
    assert counts == {"invited": 1, "failed": 1}
    assert [row.candidate_id for row in failed] == ["c-2"]
    assert to_report[0].id == first.id and to_report[1].member_id == "m-1"
    assert reported is None


def test_an_invite_cut_off_midway_can_be_claimed_again_after_a_while(run):
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from app.models.ats import AtsCandidate
    from app.storage.db import Session

    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        row = await ats_candidates.add(connection.id, None, interview, "c-1", "a@x.com")
        first = await ats_candidates.claim(row.id, (CandidateStatus.WAITING,))
        # Started just now: not stale, so nobody else may claim it.
        fresh = await ats_candidates.claim(row.id, (CandidateStatus.WAITING,))
        stale_before = [item for item in await ats_candidates.stale() if item.id == row.id]

        async with Session() as session:
            await session.execute(
                update(AtsCandidate)
                .where(AtsCandidate.id == row.id)
                .values(claimed_at=datetime.now(UTC) - timedelta(minutes=11))
            )
            await session.commit()

        stale_after = [item for item in await ats_candidates.stale() if item.id == row.id]
        again = await ats_candidates.claim(row.id, (CandidateStatus.WAITING,))
        await ats.delete_company(company)

        return first, fresh, stale_before, stale_after, again

    first, fresh, stale_before, stale_after, again = run(scenario())

    assert (first, fresh) == (True, False)
    assert stale_before == [] and len(stale_after) == 1
    assert again is True


def test_a_greenhouse_event_finds_its_linked_job_by_connection_and_job_id(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.GREENHOUSE, "…1234", "sealed", "ann")
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        greenhouse = await ats.connection(company, AtsProvider.GREENHOUSE)
        workable = await ats.connection(company, AtsProvider.WORKABLE)
        link_id = await ats.add_link(greenhouse.id, interview, JOB, STAGE)
        found = await ats.link_for_job(greenhouse.id, "A1")
        other_job = await ats.link_for_job(greenhouse.id, "B2")
        other_ats = await ats.link_for_job(workable.id, "A1")
        await ats.delete_company(company)

        return link_id, found, other_job, other_ats

    link_id, found, other_job, other_ats = run(scenario())

    assert found.id == link_id and found.stage_id == "assessment"
    assert (other_job, other_ats) == (None, None)
