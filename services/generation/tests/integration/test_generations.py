from datetime import UTC, datetime, timedelta

from app.constants.statuses import Status
from app.storage import generations


def test_a_saved_generation_reads_back(run):
    async def scenario():
        created = await generations.create("ann", "Senior Python developer")

        return await generations.get(created.id)

    found = run(scenario())

    assert (found.owner_uid, found.text, found.status) == (
        "ann",
        "Senior Python developer",
        Status.QUEUED,
    )


def test_only_queued_or_running_generations_untouched_for_long_are_failed(run):
    async def scenario():
        stuck = await generations.create("ann", "stuck")
        done = await generations.create("ann", "done")
        await generations.update(done.id, status=Status.DONE)
        failed = await generations.fail_stuck(datetime.now(UTC) + timedelta(seconds=1), "stopped")
        # Nothing new has stalled since, so a second sweep changes nothing.
        again = await generations.fail_stuck(datetime.now(UTC) - timedelta(hours=1), "stopped")

        return (
            [row.id for row in failed],
            again,
            stuck.id,
            await generations.get(stuck.id),
            await generations.get(done.id),
        )

    failed, again, stuck_id, stuck, done = run(scenario())

    # Other tests' queued generations share the database; this one is among those failed.
    assert stuck_id in failed
    assert again == []
    assert (stuck.status, stuck.error) == (Status.FAILED, "stopped")
    assert done.status == Status.DONE
