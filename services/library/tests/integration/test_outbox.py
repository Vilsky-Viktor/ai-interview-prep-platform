from sqlalchemy import select

from app.models.outbox import OutboxEvent
from app.storage import shares
from app.storage.db import Session
from tests.integration.factories import preparation


def test_a_share_invite_and_its_email_event_are_saved_together(run):
    async def scenario():
        set_id = await preparation("Shared")
        invite = await shares.upsert(set_id, "bob@example.com", "owner", "Shared", "Ann", "en")

        async with Session() as session:
            events = list(
                await session.scalars(
                    select(OutboxEvent).where(OutboxEvent.event_type == "preparation.shared")
                )
            )

        return invite, [event.data for event in events]

    invite, events = run(scenario())

    assert {
        "share_id": str(invite.id),
        "email": "bob@example.com",
        "token": invite.token,
        "title": "Shared",
        "inviter": "Ann",
        "language": "en",
    } in events
