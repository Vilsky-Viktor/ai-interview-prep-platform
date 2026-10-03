import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.models.rounds import Round
from app.storage import rounds
from app.storage.db import Session as Db
from tests.integration.factories import topic


def public(author="bob"):
    item = topic()
    item.public_author_id = author

    return item


async def backdate(round_id, days):
    async with Db() as db:
        await db.execute(
            update(Round)
            .where(Round.id == round_id)
            .values(started_at=datetime.now(UTC) - timedelta(days=days))
        )
        await db.commit()


def test_only_public_topics_first_started_today_count(run):
    user = f"user-{uuid.uuid4()}"

    async def scenario():
        today_a, today_b, older, own = public(), public(), public(), topic()
        await rounds.create(user, today_a, {})
        await rounds.create(user, today_a, {})
        await rounds.create(user, today_b, {})
        first = await rounds.create(user, older, {})
        await backdate(first.id, 2)
        # Continued today, but first started two days ago: not new today.
        await rounds.create(user, older, {})
        await rounds.create(user, own, {})
        midnight = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        return (
            await rounds.public_topics_started_since(user, midnight),
            await rounds.has_started(user, older.id),
            await rounds.has_started(user, uuid.uuid4()),
        )

    assert run(scenario()) == (2, True, False)
