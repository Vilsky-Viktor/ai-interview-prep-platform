import random

from app.storage import similar, templates
from tests.integration.factories import DIMENSIONS, direction, interview


def test_a_company_test_is_matched_with_templates_by_copy_and_by_meaning(run):
    async def scenario():
        # Directions of their own on every run, so earlier runs' templates never match.
        axis = random.randrange(100, DIMENSIONS - 1)
        close = direction(*([0.0] * axis), 1.0)
        far = direction(*([0.0] * (axis + 1)), 1.0)
        source = await interview("Ledger keeper", template=True, questions=6)
        alike = await interview("Accountant", template=True, embedding=close)
        unrelated = await interview("Nurse", template=True, embedding=far)
        copied = await templates.copy_template(source, "company-5")
        generated = await interview("Our accountant", embedding=close)

        return (
            source,
            alike,
            unrelated,
            await similar.similar_templates(copied.id, 5),
            await similar.similar_templates(generated, 5),
        )

    source, alike, unrelated, for_copy, for_generated = run(scenario())

    assert for_copy[0] == source
    # Earlier runs may share the direction; the unrelated template never matches.
    assert alike in for_generated
    assert unrelated not in for_generated


def test_one_shared_skill_isnt_the_same_role(run):
    async def scenario():
        axis = random.randrange(100, DIMENSIONS - 3)
        shared = direction(*([0.0] * axis), 1.0)
        backend = direction(*([0.0] * (axis + 1)), 1.0)
        frontend = direction(*([0.0] * (axis + 2)), 1.0)
        # A frontend template sharing only "Git" with a backend test.
        template = await interview(
            "Frontend developer", topic_embeddings=[shared, frontend, frontend], template=True
        )
        test = await interview("Backend engineer", topic_embeddings=[shared, backend, backend])

        return template, await similar.similar_templates(test, 5)

    template, found = run(scenario())

    assert template not in found
