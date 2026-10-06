import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.models.sessions import Session
from app.storage import running, sessions
from app.storage.db import Session as Db
from tests.integration.factories import topic


async def shown(row, ago):
    async with Db() as db:
        await db.execute(
            update(Session)
            .where(Session.id == row.id)
            .values(question_shown_at=datetime.now(UTC) - ago)
        )
        await db.commit()


def test_running_counts_candidates_with_a_question_on_screen_now(run):
    async def scenario():
        before = await running.running_interviews()
        invite = uuid.uuid4()
        both = await sessions.create_many("ann", invite, [topic(), topic()], 30)
        [idle] = await sessions.create_many("bob", uuid.uuid4(), [topic()], 30)
        [preview] = await sessions.create_many("cto", uuid.uuid4(), [topic()], 30, preview=True)
        await sessions.create_many("dan", uuid.uuid4(), [topic()], 30)

        for row in both:
            await shown(row, timedelta(minutes=1))

        await shown(idle, timedelta(hours=1))
        await shown(preview, timedelta(minutes=1))

        return await running.running_interviews() - before

    # Ann's interview once for its two sections; Bob left an hour ago, the preview doesn't
    # count and Dan has no question on screen.
    assert run(scenario()) == 1
