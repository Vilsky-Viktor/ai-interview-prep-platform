from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.constants.roles import Role
from app.models.companies import Company, Member
from app.storage.db import Session


async def create(name: str, user_id: str, email: str) -> Company:
    company = Company(
        name=name,
        members=[
            Member(user_id=user_id, invited_email=email.lower(), role=Role.OWNER)
        ],
    )

    async with Session() as session:
        session.add(company)
        await session.commit()

    return company


async def get(company_id) -> Company | None:
    async with Session() as session:
        return await session.get(Company, company_id, options=[selectinload(Company.members)])


async def delete(company_id) -> None:
    async with Session() as session:
        await session.execute(delete(Company).where(Company.id == company_id))
        await session.commit()


async def list_for_user(user_id: str) -> list[Company]:
    query = (
        select(Company)
        .join(Member, Member.company_id == Company.id)
        .where(Member.user_id == user_id)
        .options(selectinload(Company.members))
        .order_by(Company.created_at)
    )

    async with Session() as session:
        return list((await session.scalars(query)).unique())
