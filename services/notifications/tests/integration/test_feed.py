import asyncio
import uuid

import pytest
from prepza_common.notifications import (
    NOTIFICATION_REQUESTED,
    NotificationKind,
    Recipient,
    notification,
)

from app.constants.notifications import DROPDOWN_LIMIT
from app.integrations import companies
from app.services import events, feed
from app.storage import notifications
from tests.integration.factories import company, finished


@pytest.fixture
def member_of(monkeypatch):
    """The companies a user belongs to, as the companies service would answer."""
    memberships = {}

    async def company_ids(user_id):
        return memberships.get(user_id, [])

    monkeypatch.setattr(companies, "company_ids", company_ids)

    return memberships


def own(user_id: str, title: str) -> dict:
    return notification(
        Recipient.USER, user_id, NotificationKind.REFERRAL_REWARDED, "/billing", title=title
    )


def test_the_feed_holds_the_users_and_their_companies_notifications(run, member_of):
    user, mine, other = f"u-{uuid.uuid4()}", company(), company()
    member_of[user] = [mine]

    async def scenario():
        await notifications.add(str(uuid.uuid4()), own(user, "credits"))
        await notifications.add(str(uuid.uuid4()), finished(mine))
        await notifications.add(str(uuid.uuid4()), finished(other))

        return await feed.feed(user)

    result = run(scenario())

    assert [(item.kind, item.link) for item in result.items] == [
        ("candidate_finished", f"/companies/{mine}"),
        ("referral_rewarded", "/billing"),
    ]
    assert result.unread == 2


def test_the_dropdown_shows_the_latest_few(run, member_of):
    user = f"u-{uuid.uuid4()}"

    async def scenario():
        for number in range(DROPDOWN_LIMIT + 2):
            await notifications.add(str(uuid.uuid4()), own(user, str(number)))

        return await feed.feed(user)

    result = run(scenario())

    assert [item.data["title"] for item in result.items] == [
        str(number) for number in range(DROPDOWN_LIMIT + 1, 1, -1)
    ]
    assert result.unread == DROPDOWN_LIMIT + 2


def test_opening_the_bell_reads_everything_so_far_for_that_user_only(run, member_of):
    ann, bob, shared = f"u-{uuid.uuid4()}", f"u-{uuid.uuid4()}", company()
    member_of.update({ann: [shared], bob: [shared]})

    async def scenario():
        await notifications.add(str(uuid.uuid4()), finished(shared, "Backend"))
        await notifications.mark_seen(ann)
        after_seen = (await feed.feed(ann)).unread
        await notifications.add(str(uuid.uuid4()), finished(shared, "Frontend"))

        return after_seen, (await feed.feed(ann)).unread, (await feed.feed(bob)).unread

    assert run(scenario()) == (0, 1, 2)


def test_a_deleted_account_takes_only_its_own_notifications(run, member_of):
    user, mine = f"u-{uuid.uuid4()}", company()

    async def scenario():
        await notifications.add(str(uuid.uuid4()), own(user, "credits"))
        await notifications.add(str(uuid.uuid4()), finished(mine))
        exported = await notifications.latest([(Recipient.USER, user)], limit=None)
        await notifications.remove_user(user)
        left = await notifications.latest(
            [(Recipient.USER, user), (Recipient.COMPANY, mine)], limit=None
        )

        return [row.kind for row in exported], [row.kind for row in left]

    assert run(scenario()) == (["referral_rewarded"], ["candidate_finished"])


def test_an_open_tab_hears_of_a_new_notification_through_redis(run, member_of):
    user, mine = f"u-{uuid.uuid4()}", company()
    member_of[user] = [mine]

    async def scenario():
        stream = feed.changes(user)

        try:
            connected = await anext(stream)
            # The tab subscribed on the first step; now a notification comes for its company.
            await events.handle(NOTIFICATION_REQUESTED, finished(mine), str(uuid.uuid4()))
            # Heartbeat comments may come first (the subscriptions' own confirmations).
            heard = await asyncio.wait_for(anext(stream), 5)

            while heard.startswith(":"):
                heard = await asyncio.wait_for(anext(stream), 5)
        finally:
            await stream.aclose()

        return connected, heard

    assert run(scenario()) == (": connected\n\n", 'data: {"new": true}\n\n')
