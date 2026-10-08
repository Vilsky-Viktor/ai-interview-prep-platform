import uuid

from app.constants.ats import AtsProvider, CandidateStatus, FailReason
from app.storage import ats, ats_candidates

JOB = {"id": "A1", "name": "Accountant"}
STAGE = {"id": "assessment", "name": "Assessment"}


def test_the_recovery_job_finds_waiting_candidates_of_working_connections_oldest_first(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        await ats.connect(company, AtsProvider.GREENHOUSE, "…1234", "sealed", "ann")
        working = await ats.connection(company, AtsProvider.WORKABLE)
        broken = await ats.connection(company, AtsProvider.GREENHOUSE)
        await ats.mark_broken(broken.id)
        await ats_candidates.add(working.id, None, interview, "first", "a@x.com")
        await ats_candidates.add(working.id, None, interview, "second", "b@x.com")
        await ats_candidates.add(broken.id, None, interview, "broken", "c@x.com")
        invited = await ats_candidates.add(working.id, None, interview, "invited", "d@x.com")
        await ats_candidates.settle(invited.id, CandidateStatus.INVITED, invite_id=uuid.uuid4())
        found = [row.candidate_id for row in await ats_candidates.recoverable()]
        await ats.delete_company(company)

        return found

    found = run(scenario())

    assert [item for item in found if item in ("first", "second", "broken", "invited")] == [
        "first",
        "second",
    ]


def test_invite_again_and_a_top_up_put_not_invited_candidates_back_to_waiting(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        link_id = await ats.add_link(connection.id, interview, JOB, STAGE)
        rows = {}

        for name, reason in (("limit", FailReason.LIMIT), ("credits", FailReason.CREDITS)):
            rows[name] = await ats_candidates.add(connection.id, link_id, interview, name, "a@x")
            await ats_candidates.postpone(rows[name].id)
            await ats_candidates.settle(rows[name].id, CandidateStatus.FAILED, reason)

        topped_up = await ats_candidates.short_of_credits(company)
        await ats_candidates.settle(rows["credits"].id, CandidateStatus.FAILED, "credits")
        retried = await ats_candidates.not_invited(company, link_id)
        await ats.delete_company(company)

        return topped_up, retried

    topped_up, retried = run(scenario())

    # Each put back to waiting, with its attempts reset; a top-up only those short of credits.
    assert [(row.candidate_id, row.status, row.reason, row.attempts) for row in topped_up] == [
        ("credits", "waiting", None, 0)
    ]
    assert sorted((row.candidate_id, row.status, row.attempts) for row in retried) == [
        ("credits", "waiting", 0),
        ("limit", "waiting", 0),
    ]


def test_an_invite_failed_in_passing_waits_with_one_attempt_more(run):
    async def scenario():
        company = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed", "ann")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        row = await ats_candidates.add(connection.id, None, uuid.uuid4(), "c-1", "a@x.com")
        await ats_candidates.claim(row.id, (CandidateStatus.WAITING,))
        await ats_candidates.postpone(row.id)
        await ats_candidates.claim(row.id, (CandidateStatus.WAITING,))
        await ats_candidates.postpone(row.id)
        found = [item for item in await ats_candidates.recoverable() if item.id == row.id]
        await ats.delete_company(company)

        return found

    [found] = run(scenario())

    assert (found.status, found.attempts) == ("waiting", 2)


def test_results_kept_while_broken_are_found_once_reconnected_and_sent_once(run):
    async def scenario():
        company = uuid.uuid4()
        invite = uuid.uuid4()
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed-1", "ann", "m-1")
        connection = await ats.connection(company, AtsProvider.WORKABLE)
        row = await ats_candidates.add(connection.id, None, uuid.uuid4(), "c-1", "a@x.com")
        await ats_candidates.settle(row.id, CandidateStatus.INVITED, invite_id=invite)
        await ats.mark_broken(connection.id)
        await ats_candidates.keep_result(row.id, {"candidate_invite_id": str(invite)})
        results = [await ats_candidates.unreported()]
        await ats.connect(company, AtsProvider.WORKABLE, "acme", "sealed-2", "ann", "m-1")
        results.append(await ats_candidates.unreported())
        await ats_candidates.mark_reported(row.id)
        results.append(await ats_candidates.unreported())
        await ats.delete_company(company)
        mine = [[item.result for item in found if item.id == row.id] for found in results]

        return invite, mine

    invite, (while_broken, reconnected, after) = run(scenario())

    assert while_broken == [] and after == []
    assert reconnected == [{"candidate_invite_id": str(invite)}]


def test_a_failed_reconnect_puts_the_earlier_connection_back_marked_broken(run):
    async def scenario():
        company = uuid.uuid4()
        interview = uuid.uuid4()
        await ats.connect(company, AtsProvider.BREEZY, "Acme", "sealed-1", "ann", "m-1")
        earlier = await ats.connection(company, AtsProvider.BREEZY)
        await ats.add_link(earlier.id, interview, JOB, STAGE)
        await ats.connect(company, AtsProvider.BREEZY, "Other", "sealed-2", "bob")
        await ats.restore_broken(earlier)
        found = await ats.connection(company, AtsProvider.BREEZY)
        links = await ats.links(company)
        await ats.delete_company(company)

        return earlier, found, links

    earlier, found, links = run(scenario())

    assert found.id == earlier.id
    assert (found.account, found.credentials, found.created_by, found.member_id) == (
        "Acme",
        "sealed-1",
        "ann",
        "m-1",
    )
    assert found.status == "broken"
    assert len(links) == 1
