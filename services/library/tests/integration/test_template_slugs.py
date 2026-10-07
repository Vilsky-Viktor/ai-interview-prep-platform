import uuid

from alembic import command
from alembic.config import Config
from sqlalchemy import select

from app.constants.sets import Stage
from app.models.sets import QuestionSet
from app.storage import preparations, templates
from tests.integration.factories import direction, interview


def test_a_template_gets_a_free_slug_and_is_found_by_it(run):
    word = uuid.uuid4().hex[:8]

    async def scenario():
        first = await interview(f"Lookup {word}", template=True)
        second = await interview(f"Lookup {word}", template=True)
        company = await interview(f"Lookup {word}")

        return (
            (await templates.get_by_slug(f"lookup-{word}")).id,
            (await templates.get_by_slug(f"lookup-{word}-2")).id,
            first,
            second,
            (await preparations.get(company)).slug,
        )

    by_slug, by_second_slug, first, second, company_slug = run(scenario())

    assert (by_slug, by_second_slug) == (first, second)
    assert company_slug is None


def test_the_migration_gives_existing_templates_unique_slugs_oldest_first(run):
    word = uuid.uuid4().hex[:8]

    async def create():
        return [await interview(f"Backfill {word}", template=True) for _ in range(3)]

    async def slugs():
        from app.storage.db import Session

        async with Session() as session:
            rows = await session.execute(select(QuestionSet.id, QuestionSet.slug))

            return dict(rows.all())

    ids = run(create())
    config = Config("alembic.ini")
    command.downgrade(config, "0020")
    command.upgrade(config, "head")
    found = run(slugs())

    assert [found[set_id] for set_id in ids] == [
        f"backfill-{word}",
        f"backfill-{word}-2",
        f"backfill-{word}-3",
    ]
    template_slugs = [slug for slug in found.values() if slug is not None]
    assert len(template_slugs) == len(set(template_slugs))


def test_the_sample_has_at_most_ten_revealed_questions_spread_across_topics(run):
    async def scenario():
        template = await interview(
            "Sample", template=True, questions=30, topic_embeddings=[direction(1), direction(0, 1)]
        )
        empty = await interview("Sample empty", template=True, questions=2)

        return (
            await templates.sample_questions(template, 10),
            await templates.sample_questions(empty, 10),
        )

    sample, empty = run(scenario())

    assert len(sample) == 10
    assert all(question.stage == Stage.REVEALED for question, _ in sample)
    assert [topic for _, topic in sample[:4]] == ["Python 0", "Python 1", "Python 0", "Python 1"]
    assert empty == []
