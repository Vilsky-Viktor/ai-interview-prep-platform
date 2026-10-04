# Aliased: this module's own delete() would otherwise shadow it.
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.constants.roles import Role
from app.models.companies import Company, Member
from app.storage.db import Session

# The unique index on company names (see models/companies.py).
NAME_INDEX = "uq_companies_lower_name"


async def create(name: str, user_id: str, email: str) -> Company | None:
    """None when another company already has the name, in any case; the database decides, so
    two people creating the same name at once can't both get it."""
    company = Company(
        name=name,
        members=[Member(user_id=user_id, invited_email=email.lower(), role=Role.OWNER)],
    )

    async with Session() as session:
        session.add(company)

        try:
            await session.commit()
        except IntegrityError as error:
            if NAME_INDEX in str(error.orig):
                return None

            raise

    return company


async def owned_count(user_id: str) -> int:
    query = (
        select(func.count())
        .select_from(Member)
        .where(Member.user_id == user_id, Member.role == Role.OWNER)
    )

    async with Session() as session:
        return await session.scalar(query)


async def ids_for_user(user_id: str) -> list[str]:
    """Every company the user is a member of."""
    query = select(Member.company_id).where(Member.user_id == user_id)

    async with Session() as session:
        return [str(company_id) for company_id in await session.scalars(query)]


async def get(company_id) -> Company | None:
    async with Session() as session:
        return await session.get(Company, company_id, options=[selectinload(Company.members)])


async def delete(company_id) -> None:
    async with Session() as session:
        await session.execute(sql_delete(Company).where(Company.id == company_id))
        await session.commit()


async def list_for_user(user_id: str, offset: int, limit: int) -> list[Company]:
    query = (
        select(Company)
        .join(Member, Member.company_id == Company.id)
        .where(Member.user_id == user_id)
        .options(selectinload(Company.members))
        .order_by(Company.created_at, Company.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list((await session.scalars(query)).unique())
