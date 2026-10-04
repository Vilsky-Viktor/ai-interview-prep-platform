from app.constants.credits import LOW_BALANCE
from app.models.billing import Entry, Wallet
from app.schemas.billing import BalanceOut, EntryOut


def balance_out(row: Wallet) -> BalanceOut:
    available = row.balance - row.reserved

    return BalanceOut(
        balance=row.balance,
        reserved=row.reserved,
        available=available,
        low=available < LOW_BALANCE[row.owner_type],
        free_kits=row.free_kits,
    )


def entry_out(row: Entry) -> EntryOut:
    return EntryOut(amount=row.amount, reason=row.reason, note=row.note, created_at=row.created_at)
