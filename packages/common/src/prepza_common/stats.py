"""The admin zone's stats: each service counts its own records, all time or in one UTC month,
and answers in one shape, which the stats tab puts together."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# The month asked for, "2026-10"; None for all time.
Month = Annotated[str | None, Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]


class StatsOut(BaseModel):
    counts: dict[str, int]
    # The currency of amounts in cents, for the service that has any.
    currency: str | None = None


def month_range(month: str) -> tuple[datetime, datetime]:
    """The first moment of the UTC month "2026-10" and of the month after it."""
    year, number = (int(part) for part in month.split("-"))
    start = datetime(year, number, 1, tzinfo=UTC)
    end = datetime(year + number // 12, number % 12 + 1, 1, tzinfo=UTC)

    return start, end


async def counted(
    session: AsyncSession, value: ColumnElement, at: ColumnElement, month: str | None, *where
) -> int:
    """`value` (a count or a sum) over the rows matching `where`: every one, or those whose `at`
    is in `month`."""
    if month:
        start, end = month_range(month)
        where = (*where, at >= start, at < end)

    return int(await session.scalar(select(func.coalesce(value, 0)).where(*where)))
