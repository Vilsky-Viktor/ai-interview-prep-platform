import uuid
from datetime import UTC, datetime, timedelta

from app.storage import candidates, companies, interviews, invites


def test_a_changed_candidate_comes_last_and_a_cursor_never_repeats_or_skips_one(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        found = await interviews.create(company.id, uuid.uuid4(), "en")
        since = datetime.now(UTC) - timedelta(seconds=1)
        made = []

        for email in ("ann@example.com", "ben@example.com", "cid@example.com"):
            invite, _ = await invites.upsert(found.id, email, "Backend", "Acme", "en")
            made.append(invite)

        # Ann changes after the others were invited: the trigger moves her to the end.
        await candidates.set_name(made[0].id, "Ann Lee")

        def page(since, after=None):
            return candidates.page(found.id, 0, 2, False, since=since, after=after)

        first = await page(since)
        # The next page starts after the last one got: its time and id.
        rest = await page(first[-1].updated_at, first[-1].id)
        later = await candidates.page(
            found.id, 0, 10, False, since=datetime.now(UTC) + timedelta(minutes=1)
        )
        renamed = await candidates.get(found.id, made[0].id)

        return made, first, rest, later, renamed

    made, first, rest, later, renamed = run(scenario())
    emails = [invite.email for invite in first + rest]

    assert emails == ["ben@example.com", "cid@example.com", "ann@example.com"]
    assert later == []
    assert renamed.updated_at > made[0].updated_at


def test_an_interview_changed_since_is_listed_oldest_change_first(run):
    async def scenario():
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        since = datetime.now(UTC) - timedelta(seconds=1)
        older = await interviews.create(company.id, uuid.uuid4(), "en")
        newer = await interviews.create(company.id, uuid.uuid4(), "en")
        await interviews.set_title(older.id, "Renamed")
        listed = await interviews.list_for_company(company.id, 0, 10, since)

        return [row.id for row in listed], older.id, newer.id

    listed, older, newer = run(scenario())

    assert listed == [newer, older]
