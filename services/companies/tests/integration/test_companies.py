from app.storage import companies


def test_company_names_are_unique_ignoring_case_until_deleted(run):
    async def scenario():
        first = await companies.create("Unique Co", "ann", "ann@example.com")
        taken = await companies.create("unique co", "bob", "bob@example.com")
        await companies.delete(first.id)
        freed = await companies.create("UNIQUE CO", "bob", "bob@example.com")

        return first, taken, freed

    first, taken, freed = run(scenario())

    assert first is not None
    assert taken is None
    assert freed is not None and freed.name == "UNIQUE CO"
