import uuid

from app.storage import accounts, sessions, talents
from tests.integration.factories import topic


def test_a_link_is_saved_updated_withdrawn_and_goes_with_the_account(run):
    user = f"talent-{uuid.uuid4()}"
    other = f"talent-{uuid.uuid4()}"

    async def scenario():
        await talents.save(user, "Ann", "https://linkedin.com/in/ann")
        updated = await talents.save(user, "Ann Lee", "https://www.linkedin.com/in/ann-lee")
        await talents.save(user, "Ann Lee", None)
        withdrawn = await talents.get(user)
        await talents.save(other, "Bob", "https://www.linkedin.com/in/bob")
        await accounts.delete_user(other)

        return updated, withdrawn, await talents.get(other)

    updated, withdrawn, deleted = run(scenario())

    assert (updated.name, updated.url) == ("Ann Lee", "https://www.linkedin.com/in/ann-lee")
    # Withdrawn, the answer stays (they aren't asked again), without the link.
    assert withdrawn.url is None
    assert deleted is None


def test_only_talents_who_agreed_are_found_for_suggestions(run):
    agreed = f"talent-{uuid.uuid4()}"
    declined = f"talent-{uuid.uuid4()}"

    async def scenario():
        practice_topic = topic(2)
        template_id = practice_topic.preparation_id
        await talents.save(agreed, "Ann", "https://www.linkedin.com/in/ann")
        await talents.save(declined, "Bob", None)

        for user in (agreed, declined):
            await sessions.create_many(user, uuid.uuid4(), [practice_topic], 60, practice=True)

        return await talents.practice_of_consenting([template_id])

    rows, links = run(scenario())

    assert {row.user_id for row in rows} == {agreed}
    assert agreed in links and declined not in links
