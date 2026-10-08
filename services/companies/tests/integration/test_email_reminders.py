"""What notifications reads for its digest and reminders: members, and interviews waiting."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.models.interviews import Interview
from app.storage import companies, email_reminders, interviews, invites
from app.storage.db import Session


async def company():
    return await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")


async def ready_at(interview_id, when):
    async with Session() as session:
        await session.execute(
            update(Interview).where(Interview.id == interview_id).values(ready_at=when)
        )
        await session.commit()


def test_an_interview_is_ready_when_it_gets_its_questions_once(run):
    async def scenario():
        found = await company()
        generated = await interviews.create(found.id, uuid.uuid4(), "en")
        before = (await interviews.get(generated.id)).ready_at
        await interviews.set_generated(
            generated.generation_id, uuid.uuid4(), "Backend", {}, str(uuid.uuid4())
        )
        first = (await interviews.get(generated.id)).ready_at
        # Regenerated questions don't move it.
        await interviews.set_generated(
            generated.generation_id, uuid.uuid4(), "Backend", {}, str(uuid.uuid4())
        )
        second = (await interviews.get(generated.id)).ready_at
        template = await interviews.create_from_template(found.id, uuid.uuid4(), "Design", "en")

        return before, first, second, (await interviews.get(template.id)).ready_at

    before, first, second, template = run(scenario())

    assert before is None
    assert first is not None and second == first
    assert template is not None


def test_waiting_interviews_are_ready_ones_nobody_was_invited_to_and_ones_still_generating(run):
    now = datetime.now(UTC)

    async def scenario():
        found = await company()
        idle = await interviews.create_from_template(found.id, uuid.uuid4(), "Idle", "en")
        invited = await interviews.create_from_template(found.id, uuid.uuid4(), "Invited", "en")
        recent = await interviews.create_from_template(found.id, uuid.uuid4(), "Recent", "en")
        hired = await interviews.create_from_template(found.id, uuid.uuid4(), "Hired", "en")
        generating = await interviews.create(found.id, uuid.uuid4(), "en")
        await invites.upsert(invited.id, "gus@example.com", "Invited", "Acme", "en")

        for interview in (idle, invited, hired):
            await ready_at(interview.id, now - timedelta(days=4))

        async with Session() as session:
            await session.execute(
                update(Interview).where(Interview.id == hired.id).values(hired=True)
            )
            await session.commit()

        without = await email_reminders.without_candidates(
            now - timedelta(days=10), now - timedelta(days=3)
        )
        being = await email_reminders.being_generated(
            now - timedelta(days=15), now + timedelta(minutes=1)
        )
        ids = {idle.id, invited.id, recent.id, hired.id, generating.id}

        return (
            {row.id for row in without} & ids,
            {row.id for row in being} & ids,
            idle.id,
            generating.id,
        )

    without, being, idle, generating = run(scenario())

    assert without == {idle}
    assert being == {generating}


def test_members_come_with_their_company_and_whether_they_can_act(run):
    async def scenario():
        found = await company()

        return found.id, await email_reminders.with_members([found.id, uuid.uuid4()])

    company_id, found = run(scenario())

    [only] = found
    assert only.id == company_id
    assert [(member.user_id, member.role) for member in only.members] == [("owner", "owner")]
