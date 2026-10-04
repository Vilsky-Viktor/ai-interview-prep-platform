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


def test_the_library_filters_by_level_and_language_and_sorts(run):
    from sqlalchemy import update

    from app.models.sets import QuestionSet
    from app.storage.db import Session

    async def scenario():
        older = await preparation("Zeta Older", level="basic", language="en")
        await preparation("Zeta German", level="hard", language="de")
        newer = await preparation("Zeta Newer", level="basic", language="ru")

        # The older kit has more joiners; the newer one is, well, newer.
        async with Session() as session:
            await session.execute(
                update(QuestionSet).where(QuestionSet.id == older).values(join_count=5)
            )
            await session.execute(
                update(QuestionSet).where(QuestionSet.id == newer).values(join_count=1)
            )
            await session.commit()

        async def titles(**options):
            rows = await search.search_public("zeta", 0, 10, **options)

            return [row[0].title for row in rows]

        return (
            await titles(level="basic", languages=["en", "ru"], sort="date"),
            await titles(level="basic", languages=["en", "ru"], sort="joiners"),
            await titles(languages=["de"]),
        )

    by_date, by_joiners, german = run(scenario())

    assert by_date == ["Zeta Newer", "Zeta Older"]
    assert by_joiners == ["Zeta Older", "Zeta Newer"]
    assert german == ["Zeta German"]
