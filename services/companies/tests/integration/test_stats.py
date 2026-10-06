import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.constants.verification import VerificationStatus
from app.models.companies import Company
from app.storage import companies, interviews, invites, stats
from app.storage.db import Session


async def set_company(company_id, **values):
    async with Session() as session:
        await session.execute(update(Company).where(Company.id == company_id).values(**values))
        await session.commit()


def test_counts_only_what_the_month_added(run):
    now = datetime.now(UTC)
    month = now.strftime("%Y-%m")

    async def scenario():
        before, before_all = await stats.stats(month), await stats.stats(None)
        company = await companies.create(f"Acme {uuid.uuid4()}", "owner", "owner@example.com")
        found = await interviews.create(company.id, uuid.uuid4(), "en")
        finished = await invites.for_link(found.id, "done@example.com")
        await invites.finish(finished.id, 80, False, None)
        await invites.for_link(found.id, "waiting@example.com")
        await set_company(
            company.id,
            verification_status=VerificationStatus.APPROVED,
            verification_decided_at=now,
        )
        # Created last month: not this month's.
        older = await companies.create(f"Older {uuid.uuid4()}", "owner", "owner@example.com")
        await set_company(older.id, created_at=now.replace(day=1) - timedelta(days=1))
        after, after_all = await stats.stats(month), await stats.stats(None)

        return (
            {name: after[name] - before[name] for name in after},
            after_all["companies"] - before_all["companies"],
        )

    this_month, all_time = run(scenario())

    # All time has last month's company too.
    assert all_time == 2
    assert this_month == {
        "companies": 1,
        "verified": 1,
        "interviews": 1,
        "invited": 2,
        "finished": 1,
    }
