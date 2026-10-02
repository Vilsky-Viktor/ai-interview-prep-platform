from app.storage import search
from tests.integration.factories import preparation


def test_search_finds_public_preparations_by_title_or_topic(run):
    async def scenario():
        await preparation("Rust Systems", topic="Ownership and borrowing")
        await preparation("Rust Private", topic="Ownership and borrowing", public=False)
        await preparation("Cooking", topic="Knife skills")

        by_topic = await search.search_public("borrowing", 0, 10)
        by_title = await search.search_public("cook", 0, 10)

        return [row[0].title for row in by_topic], [row[0].title for row in by_title]

    by_topic, by_title = run(scenario())

    assert by_topic == ["Rust Systems"]
    assert by_title == ["Cooking"]
