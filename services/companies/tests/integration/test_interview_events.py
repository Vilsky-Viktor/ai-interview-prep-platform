"""The events ats consumes are saved with their change, in the same transaction, once."""

import uuid

from sqlalchemy import select

from app.models.outbox import OutboxEvent
from app.storage import companies, interviews, invites
from app.storage.db import Session


async def interview():
    company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")

    return await interviews.create(company.id, uuid.uuid4(), "en")


async def events(event_type: str, key: str, value: str) -> list[dict]:
    """The data of the outbox's events of that type whose `key` is `value`."""
    async with Session() as session:
        return list(
            await session.scalars(
                select(OutboxEvent.data).where(
                    OutboxEvent.event_type == event_type, OutboxEvent.data[key].astext == value
                )
            )
        )


def test_a_finished_candidate_delivered_twice_is_announced_once(run):
    async def scenario():
        found = await interview()
        invite = await invites.upsert(found.id, "gus@example.com", "Backend", "Acme", "en")
        result = {"candidate_invite_id": str(invite.id), "grade": 70, "passed": True}
        event_id = str(uuid.uuid4())
        await invites.finish(invite.id, 70, False, None, event_id, result)
        await invites.finish(invite.id, 70, False, None, event_id, result)

        return result, await events("candidate.finished", "candidate_invite_id", str(invite.id))

    result, saved = run(scenario())

    assert saved == [result]


def test_an_interview_made_ready_twice_by_one_event_is_announced_once(run):
    async def scenario():
        found = await interview()
        event_id = str(uuid.uuid4())

        for _ in range(2):
            await interviews.set_generated(
                found.generation_id, uuid.uuid4(), "Backend", {"kind": "x"}, event_id
            )

        return found, await events("interview.ready", "interview_id", str(found.id))

    found, saved = run(scenario())

    assert saved == [{"interview_id": str(found.id)}]


def test_a_removed_interview_is_announced_once(run):
    async def scenario():
        found = await interview()
        await interviews.remove(found.id)
        await interviews.remove(found.id)

        return found, await events("interview.deleted", "interview_id", str(found.id))

    found, saved = run(scenario())

    assert saved == [{"interview_id": str(found.id), "company_id": str(found.company_id)}]


def test_a_cancelled_generations_interview_is_announced_as_deleted(run):
    async def scenario():
        found = await interview()
        await interviews.remove_for_generation(found.generation_id, {"kind": "x"})
        await interviews.remove_for_generation(found.generation_id, {"kind": "x"})

        return found, await events("interview.deleted", "interview_id", str(found.id))

    found, saved = run(scenario())

    assert saved == [{"interview_id": str(found.id), "company_id": str(found.company_id)}]


def test_interviews_by_ids_skip_the_ones_gone(run):
    async def scenario():
        kept, gone = await interview(), await interview()
        await interviews.remove(gone.id)
        found = await interviews.by_ids([kept.id, gone.id, uuid.uuid4()])

        return kept, [item.id for item in found], await interviews.by_ids([])

    kept, found, none = run(scenario())

    assert (found, none) == ([kept.id], [])


def test_a_failed_generation_marks_its_interview_once_until_the_questions_come(run):
    async def scenario():
        found = await interview()
        event_id = str(uuid.uuid4())
        await interviews.mark_failed(found.generation_id, event_id)
        failed = (await interviews.get(found.id)).generation_failed
        # Retried; the same event delivered again doesn't mark it again.
        await interviews.set_generation_failed(found.id, False)
        await interviews.mark_failed(found.generation_id, event_id)
        redelivered = (await interviews.get(found.id)).generation_failed
        # Failed again, then the retry's questions come: they clear it, and a late failure of
        # an earlier run leaves the ready interview alone.
        await interviews.mark_failed(found.generation_id, str(uuid.uuid4()))
        await interviews.set_generated(
            found.generation_id, uuid.uuid4(), "Backend", {"kind": "x"}, str(uuid.uuid4())
        )
        await interviews.mark_failed(found.generation_id, str(uuid.uuid4()))

        return failed, redelivered, await interviews.get(found.id)

    failed, redelivered, ready = run(scenario())

    assert (failed, redelivered) == (True, False)
    assert ready.generation_failed is False and ready.set_id is not None
