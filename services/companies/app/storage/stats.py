"""The admin zone's stats from companies' records: what is stored now, so deleted companies and
candidates past retention aren't counted."""

from prepza_common.stats import counted
from sqlalchemy import func

from app.constants.invites import InviteStatus
from app.constants.verification import VerificationStatus
from app.models.companies import Company
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage.db import Session


async def stats(month: str | None) -> dict[str, int]:
    """All time or in `month`: companies created and verified now (in the month approved),
    interviews created, and candidates invited and finished, both in the month they were invited."""
    invites = func.count(CandidateInvite.id)

    async with Session() as session:
        return {
            "companies": await counted(session, func.count(Company.id), Company.created_at, month),
            "verified": await counted(
                session,
                func.count(Company.id),
                Company.verification_decided_at,
                month,
                Company.verification_status == VerificationStatus.APPROVED,
            ),
            "interviews": await counted(
                session, func.count(Interview.id), Interview.created_at, month
            ),
            "invited": await counted(session, invites, CandidateInvite.created_at, month),
            "finished": await counted(
                session,
                invites,
                CandidateInvite.created_at,
                month,
                CandidateInvite.status == InviteStatus.FINISHED,
            ),
        }
