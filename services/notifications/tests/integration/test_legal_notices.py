import uuid

from app.storage import legal_notices


def test_a_versions_notice_is_asked_for_once_and_marked_sent(run):
    version = f"t{uuid.uuid4().hex[:9]}"

    async def scenario():
        first = await legal_notices.ask("terms", version, "sam")
        again = await legal_notices.ask("terms", version, "kim")
        await legal_notices.sent("terms", version)
        [row] = [row for row in await legal_notices.all_notices() if row.version == version]

        return first, again, row

    first, again, row = run(scenario())

    assert (first, again) == (True, False)
    assert row.asked_by == "sam" and row.sent_at is not None
