import uuid

from prepza_common.notifications import NotificationKind, Recipient, notification

from app.storage import notifications
from tests.integration.factories import api, company, finished, push


def test_a_deleted_companys_notifications_go_and_none_come_after(run):
    company_id, other_id = company(), company()
    deleted = push("company.deleted", {"company_id": company_id}, message_id="m-del")

    async def scenario():
        await notifications.add(str(uuid.uuid4()), finished(company_id, email="a@x.com"))
        await notifications.add(str(uuid.uuid4()), finished(other_id, email="b@x.com"))

        async with api() as client:
            # Pub/Sub may deliver it twice.
            codes = [(await client.post("/internal/events", json=deleted)).status_code]
            codes.append((await client.post("/internal/events", json=deleted)).status_code)

        # A notification that was on its way when the company went.
        late = notification(
            Recipient.COMPANY, company_id, NotificationKind.INTERVIEW_READY, "/x", title="T"
        )
        stored_late = await notifications.add(str(uuid.uuid4()), late)
        left = await notifications.latest([(Recipient.COMPANY, company_id)], limit=None)
        others = await notifications.latest([(Recipient.COMPANY, other_id)], limit=None)

        return codes, stored_late, left, others

    codes, stored_late, left, others = run(scenario())

    assert codes == [204, 204]
    assert stored_late is False
    assert left == []
    # Another company keeps its own.
    assert [item.data["email"] for item in others] == ["b@x.com"]
