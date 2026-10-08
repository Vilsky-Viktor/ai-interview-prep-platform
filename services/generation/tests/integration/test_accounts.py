import uuid
from datetime import UTC, datetime, timedelta

from prepza_common.constants import DELETED_USER

from app.constants.statuses import Status
from app.storage import accounts, generations


def test_deleting_a_user_keeps_company_tests_without_their_id(run):
    async def scenario():
        mine = await generations.create("gone", "company job", uuid.uuid4())
        other = await generations.create("stays", "someone else", uuid.uuid4())
        exported = await accounts.export("gone")

        await accounts.delete_user("gone")

        return exported, await generations.get(mine.id), await generations.get(other.id)

    exported, mine, other = run(scenario())

    assert [item["pasted_text"] for item in exported] == ["company job"]
    assert mine.owner_uid == DELETED_USER
    assert other.owner_uid == "stays"


def test_old_finished_generations_lose_their_pasted_text_only(run):
    async def scenario():
        finished = await generations.create("ann", "old finished text")
        await generations.update(finished.id, status=Status.DONE)
        running = await generations.create("ann", "still running")
        await generations.update(running.id, status=Status.RUNNING)

        count = await accounts.forget_texts(datetime.now(UTC) + timedelta(seconds=1), None)

        return count, await generations.get(finished.id), await generations.get(running.id)

    count, finished, running = run(scenario())

    assert count >= 1
    assert (finished.text, finished.status) == ("", Status.DONE)
    assert running.text == "still running"
