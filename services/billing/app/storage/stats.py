"""The admin zone's stats from billing's records. Purchases stay when an account or company is
deleted, so every top-up counts; a deleted company's spent credits go with its history."""

from prepza_common.stats import counted
from sqlalchemy import BigInteger, cast, func, select

from app.constants.credits import Reason
from app.constants.products import CURRENCY
from app.models.billing import Entry, Purchase
from app.storage.db import Session


async def stats(period: str | None) -> dict[str, int]:
    """All time or in `period` (a year or a period): paid top-ups and what they paid in cents, tax included and refunds
    not taken off, and the credits companies spent on candidates. Each product line of a transaction
    holds the whole transaction's total, so it counts once."""
    transactions = (
        select(
            func.min(Purchase.created_at).label("created_at"),
            func.max(cast(Purchase.total, BigInteger)).label("paid"),
        )
        .where(Purchase.currency == CURRENCY)
        .group_by(Purchase.transaction_id)
        .subquery()
    )

    async with Session() as session:
        return {
            "top_ups": await counted(
                session, func.count(transactions.c.created_at), transactions.c.created_at, period
            ),
            "paid": await counted(
                session, func.sum(transactions.c.paid), transactions.c.created_at, period
            ),
            "credits_spent": await counted(
                session,
                -func.sum(Entry.amount),
                Entry.created_at,
                period,
                Entry.reason == Reason.CANDIDATE,
            ),
        }
