import uuid

from app.schemas.interviews import InterviewSettings
from app.storage import companies, interviews, invites, pass_rates


async def interview(grades, pass_mark=60, unfinished=0):
    """A company's interview whose candidates finished with `grades`, and `unfinished` more."""
    company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
    found = await interviews.create(company.id, uuid.uuid4(), "en")
    await interviews.update_settings(found.id, InterviewSettings(pass_mark=pass_mark))

    for index, grade in enumerate(grades):
        invite = await invites.for_link(found.id, f"c{index}@example.com")
        await invites.finish(invite.id, grade, False, None)

    for index in range(unfinished):
        await invites.for_link(found.id, f"u{index}@example.com")

    return found.id


def mine(rows, ids):
    return [(row.finished, row.passed, float(row.average)) for row in rows if row.id in ids]


def test_rates_count_only_finished_candidates_against_each_pass_mark_sorted_in_sql(run):
    async def scenario():
        # Passed at or above the mark: 2 of 3, 1 of 2 (mark 50), none of 1.
        most = await interview([60, 59, 90], unfinished=2)
        half = await interview([50, 40], pass_mark=50)
        none = await interview([10])
        never = await interview([], unfinished=1)
        ids = [most, half, none, never]

        return (
            mine(await pass_rates.page(False, 0, 1000), ids),
            mine(await pass_rates.page(True, 0, 1000), ids),
        )

    by_rate, by_finished = run(scenario())

    # Lowest pass rate first; an interview nobody finished isn't listed.
    assert by_rate == [(1, 0, 10.0), (2, 1, 45.0), (3, 2, 69.66666666666667)]
    # Most finished first.
    assert [row[0] for row in by_finished] == [3, 2, 1]
