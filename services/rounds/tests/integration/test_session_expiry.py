import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.constants.rounds import RoundStatus
from app.models.sessions import Session
from app.services import session_expiry
from app.storage import sessions
from app.storage.db import Session as Db
from tests.integration.factories import topic


async def interview(started_minutes_ago: float):
    """A candidate's interview of two sections, 3 questions each at 60 seconds: 6 minutes in
    all, 6.6 with the margin."""
    invite_id = uuid.uuid4()
    rows = await sessions.create_many("cand", invite_id, [topic(), topic()], 60)

    async with Db() as db:
        await db.execute(
            update(Session)
            .where(Session.candidate_invite_id == invite_id)
            .values(started_at=datetime.now(UTC) - timedelta(minutes=started_minutes_ago))
        )
        await db.commit()

    return invite_id, rows


def test_an_interview_left_past_its_time_finishes_by_itself(run):
    async def scenario():
        _, expired_rows = await interview(started_minutes_ago=7)
        _, running_rows = await interview(started_minutes_ago=6)

        await session_expiry.finish_expired()

        return (
            [await sessions.get(row.id) for row in expired_rows],
            [await sessions.get(row.id) for row in running_rows],
        )

    expired, running = run(scenario())

    assert [row.status for row in expired] == [RoundStatus.FINISHED] * 2
    # Nothing was answered, so every question counts as wrong.
    assert [row.final_score for row in expired] == [0, 0]
    # Still within its time plus the 10% margin.
    assert [row.status for row in running] == [RoundStatus.IN_PROGRESS] * 2


def test_a_candidate_coming_back_late_finds_the_interview_finished(run):
    async def scenario():
        late_id, late_rows = await interview(started_minutes_ago=30)
        on_time_id, _ = await interview(started_minutes_ago=1)

        return (
            await session_expiry.finish_if_expired(late_id),
            await session_expiry.finish_if_expired(on_time_id),
            await sessions.get(late_rows[0].id),
        )

    late, on_time, row = run(scenario())

    assert (late, on_time) == (True, False)
    assert row.status == RoundStatus.FINISHED
