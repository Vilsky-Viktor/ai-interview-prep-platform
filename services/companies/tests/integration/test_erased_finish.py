import uuid

from sqlalchemy import func, select, update

from app.constants.invites import InviteStatus
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.storage import invites
from app.storage.db import Session
from tests.integration.test_invites import interview


def test_a_candidate_erased_while_finishing_stays_erased_without_events(run):
    async def scenario():
        found = await interview()
        invite, _ = await invites.upsert(found.id, "hal@example.com", "Backend", "Acme", "en")

        async with Session() as session:
            await session.execute(
                update(CandidateInvite)
                .where(CandidateInvite.id == invite.id)
                .values(status=InviteStatus.DELETED)
            )
            await session.commit()

        notice = {"kind": "candidate_finished", "invite": str(invite.id)}
        await invites.finish(
            invite.id, 70, False, notice, str(uuid.uuid4()), {"invite": str(invite.id)}
        )

        async with Session() as session:
            events = await session.scalar(
                select(func.count())
                .select_from(OutboxEvent)
                .where(OutboxEvent.data["invite"].astext == str(invite.id))
            )

        return (await invites.get(invite.id)).status, events

    assert run(scenario()) == (InviteStatus.DELETED, 0)
