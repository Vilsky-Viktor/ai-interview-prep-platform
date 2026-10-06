"""Pass rates per company interview for the superadmin's monitoring (docs/compliance/
post-market-monitoring-plan.md): counted, averaged, sorted and paged in SQL from the grade stored
on each finished invite."""

from sqlalchemy import Row, func, select

from app.constants.invites import InviteStatus
from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage.db import Session


async def page(by_finished: bool, offset: int, limit: int) -> list[Row]:
    """Interviews with finished candidates: lowest pass rate first, or most finished first.
    Each row has the interview's id, title, set_id, pass_mark, the company's name, and the
    finished, passed and average (grade) of its candidates."""
    finished = func.count(CandidateInvite.id)
    passed = func.count(CandidateInvite.id).filter(CandidateInvite.grade >= Interview.pass_mark)
    order = [finished.desc()] if by_finished else [passed * 1.0 / finished, finished.desc()]
    query = (
        select(
            Interview.id,
            Interview.title,
            Interview.set_id,
            Interview.pass_mark,
            Company.name.label("company"),
            finished.label("finished"),
            passed.label("passed"),
            func.avg(CandidateInvite.grade).label("average"),
        )
        .join(CandidateInvite, CandidateInvite.interview_id == Interview.id)
        .join(Company, Company.id == Interview.company_id)
        .where(CandidateInvite.status == InviteStatus.FINISHED, CandidateInvite.grade.is_not(None))
        .group_by(Interview.id, Company.id)
        .order_by(*order, Interview.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.execute(query))
