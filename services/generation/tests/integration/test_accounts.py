import uuid
from datetime import UTC, datetime, timedelta

from app.constants.accounts import DELETED_OWNER
from app.constants.statuses import Status
from app.storage import accounts, generations


def test_deleting_a_user_keeps_company_interviews_without_their_id(run):
    async def scenario():
        own = await generations.create("gone", "my job text")
        interview = await generations.create("gone", "company job", "interview", uuid.uuid4())
        other = await generations.create("stays", "someone else")
        exported = await accounts.export("gone")

        await accounts.delete_user("gone")

        return (
            exported,
            await generations.get(own.id),
            await generations.get(interview.id),
            await generations.get(other.id),
        )

    exported, own, interview, other = run(scenario())

    assert [item["pasted_text"] for item in exported] == ["my job text"]
    assert own is None
    assert interview.owner_uid == DELETED_OWNER
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
