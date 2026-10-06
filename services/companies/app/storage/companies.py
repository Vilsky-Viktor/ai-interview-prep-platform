# Aliased: this module's own delete() would otherwise shadow it.
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select, update
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


async def names(company_ids: list) -> dict:
    """Company names by id; deleted companies are missing."""
    if not company_ids:
        return {}

    query = select(Company.id, Company.name).where(Company.id.in_(company_ids))

    async with Session() as session:
        return {str(row.id): row.name for row in await session.execute(query)}


async def delete(company_id) -> None:
    async with Session() as session:
        await session.execute(sql_delete(Company).where(Company.id == company_id))
        await session.commit()


async def list_for_user(
    user_id: str, offset: int, limit: int, roles: tuple[str, ...] = tuple(Role)
) -> list[Company]:
    """The user's companies, only those where their role is one of `roles`."""
    query = (
        select(Company)
        .join(Member, Member.company_id == Company.id)
        .where(Member.user_id == user_id, Member.role.in_(roles))
        .options(selectinload(Company.members))
        .order_by(Company.created_at, Company.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list((await session.scalars(query)).unique())


async def set_logo(company_id, content: bytes | None, media_type: str | None) -> None:
    """Saves the company's logo, or removes it with None; either way its address changes."""
    async with Session() as session:
        await session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(logo=content, logo_type=media_type, logo_version=Company.logo_version + 1)
        )
        await session.commit()


async def get_logo(company_id) -> tuple[bytes, str] | None:
    async with Session() as session:
        row = (
            await session.execute(
                select(Company.logo, Company.logo_type).where(Company.id == company_id)
            )
        ).first()

    if row is None or row.logo is None:
        return None

    return row.logo, row.logo_type


async def rename(company_id, name: str) -> bool:
    """False when another company already has the name, in any case; the database decides."""
    async with Session() as session:
        try:
            await session.execute(update(Company).where(Company.id == company_id).values(name=name))
            await session.commit()
        except IntegrityError as error:
            if NAME_INDEX in str(error.orig):
                return False

            raise

    return True


async def set_website(company_id, domain: str | None, verified: bool) -> None:
    """The company's website domain, verified or not yet; None clears both."""
    async with Session() as session:
        await session.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(website_domain=domain, verified_domain=domain if verified else None)
        )
        await session.commit()
