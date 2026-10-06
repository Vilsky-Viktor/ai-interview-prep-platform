from datetime import datetime

from sqlalchemy import Text, delete, func, literal, or_, select, update
from sqlalchemy.orm import aliased

from app.constants.invites import InviteStatus
from app.constants.roles import Role
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.storage.db import Session


async def memberships(user_id: str) -> list[tuple[Member, Company, int]]:
    """The user's memberships, each with its company and that company's number of owners."""
    owner = aliased(Member)
    owners = (
        select(func.count())
        .where(owner.company_id == Company.id, owner.role == Role.OWNER)
        .correlate(Company)
        .scalar_subquery()
    )
    query = (
        select(Member, Company, owners)
        .join(Company, Company.id == Member.company_id)
        .where(Member.user_id == user_id)
    )

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def remove_member(member_id) -> None:
    async with Session() as session:
        await session.execute(delete(Member).where(Member.id == member_id))
        await session.commit()


async def candidate_invites(user_id: str, email: str) -> list[tuple]:
    """(interview id, email, status) of every invite the user was sent or accepted."""
    query = select(
        CandidateInvite.interview_id, CandidateInvite.email, CandidateInvite.status
    ).where(or_(CandidateInvite.user_id == user_id, CandidateInvite.email == email.lower()))

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def forget_candidate(user_id: str, email: str) -> None:
    """Keeps the company's invite row, marked deleted, without the candidate's email or a
    usable link. The email becomes unique per invite, as an interview can't hold it twice."""
    async with Session() as session:
        await session.execute(
            update(CandidateInvite)
            .where(or_(CandidateInvite.user_id == user_id, CandidateInvite.email == email.lower()))
            .values(
                status=InviteStatus.DELETED,
                email=literal("deleted-") + func.cast(CandidateInvite.id, Text()),
                token=func.md5(func.random().cast(Text()) + func.cast(CandidateInvite.id, Text())),
                user_id=None,
            )
        )
        await session.commit()


async def export(user_id: str, email: str) -> dict:
    async with Session() as session:
        companies = await session.execute(
            select(Company.name, Member.role, Member.created_at)
            .join(Member, Member.company_id == Company.id)
            .where(Member.user_id == user_id)
        )
        invites = await session.execute(
            select(Interview.title, CandidateInvite.status, CandidateInvite.created_at)
            .join(Interview, Interview.id == CandidateInvite.interview_id)
            .where(or_(CandidateInvite.user_id == user_id, CandidateInvite.email == email.lower()))
        )

        return {
            "company_memberships": [
                {"company": name, "role": role, "since": since} for name, role, since in companies
            ],
            "interview_invites": [
                {"interview": title, "status": status, "invited_at": at}
                for title, status, at in invites
            ],
        }


async def expired_invites(before: datetime) -> list:
    """Invites last sent before `before`: kept CANDIDATE_RETENTION_DAYS after the latest send,
    as the privacy policy says, so sending one again keeps its results longer."""
    async with Session() as session:
        return list(
            await session.scalars(
                select(CandidateInvite.id).where(CandidateInvite.sent_at < before)
            )
        )


async def delete_invites(invite_ids: list) -> None:
    if not invite_ids:
        return

    async with Session() as session:
        await session.execute(delete(CandidateInvite).where(CandidateInvite.id.in_(invite_ids)))
        await session.commit()
