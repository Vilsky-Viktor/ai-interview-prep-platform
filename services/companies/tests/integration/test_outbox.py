import uuid

from sqlalchemy import select

from app.models.outbox import OutboxEvent
from app.storage import companies, interviews, invites
from app.storage.db import Session


def test_a_candidate_invite_and_its_email_event_are_saved_together(run):
    async def scenario():
        company = await companies.create("Acme", "owner", "owner@example.com")
        interview = await interviews.create(company.id, uuid.uuid4())
        invite = await invites.upsert(interview.id, "erin@example.com", "Backend", "Acme")

        async with Session() as session:
            events = list(
                await session.scalars(
                    select(OutboxEvent).where(OutboxEvent.event_type == "candidate.invited")
                )
            )

        return invite, [event.data for event in events]

    invite, events = run(scenario())

    assert {
        "invite_id": str(invite.id),
        "email": "erin@example.com",
        "token": invite.token,
        "title": "Backend",
        "company": "Acme",
    } in events
