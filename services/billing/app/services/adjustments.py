import logging

from prepza_common.analytics import track

from app.constants.credits import Reason
from app.constants.products import ADJUSTMENT_APPROVED, DELETED_OWNER
from app.helpers.owners import owner_of
from app.storage import ledger, purchases

logger = logging.getLogger(__name__)

# Paddle's adjustment action, and whether it takes the credits back (-1) or returns them (+1).
ACTIONS = {
    "refund": (Reason.REFUND, -1),
    "chargeback": (Reason.CHARGEBACK, -1),
    "chargeback_reverse": (Reason.CHARGEBACK_REVERSED, 1),
}


def share(granted: int, adjusted_total: str, paid_total: str) -> int:
    """The part of the credits a payment bought that an adjustment of `adjusted_total` covers;
    a full refund is all of them."""
    paid = int(paid_total)

    if paid <= 0:
        return 0

    return granted * min(int(adjusted_total), paid) // paid


async def handle_adjustment(data: dict) -> None:
    """Takes back the credits of an approved refund or a chargeback, and returns them when a
    chargeback is reversed. Each adjustment counts once, however often Paddle sends it. The
    balance may go negative if the credits were spent; then nothing can be spent until a
    top-up covers it."""
    found = ACTIONS.get(data.get("action"))

    if found is None or data.get("status") != ADJUSTMENT_APPROVED:
        return

    reason, sign = found
    bought = await purchases.for_transaction(data["transaction_id"])

    if bought is None:
        logger.warning("Adjustment %s is for a transaction we didn't sell", data["id"])

        return

    owner_type, owner_id, granted, paid_total = bought

    # The buyer deleted their account; their wallet is gone.
    if owner_id == DELETED_OWNER:
        return

    credits = share(granted, data["totals"]["total"], paid_total)

    if credits:
        await ledger.adjust(
            owner_type, owner_id, sign * credits, f"adjustment:{data['id']}", reason
        )
        await track(
            "credits_taken_back",
            **owner_of(owner_type, owner_id),
            why=reason,
            credits=sign * credits,
        )
