from app.models.billing import Entry, Wallet
from app.schemas.billing import BalanceOut, EntryOut


def balance_out(row: Wallet) -> BalanceOut:
    return BalanceOut(
        balance=row.balance, reserved=row.reserved, available=row.balance - row.reserved
    )


def entry_out(row: Entry) -> EntryOut:
    return EntryOut(amount=row.amount, reason=row.reason, note=row.note, created_at=row.created_at)
