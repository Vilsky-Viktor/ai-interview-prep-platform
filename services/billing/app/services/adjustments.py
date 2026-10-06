import logging

from prepza_common.analytics import track

from app.constants.credits import Reason
from app.constants.products import ADJUSTMENT_APPROVED
from app.services.referrals import take_back_reward
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
    top-up covers it. Taking back all of a top-up also takes back the referral rewards it paid
    (not returned by a chargeback's reversal: the company's next top-up pays them again)."""
    found = ACTIONS.get(data.get("action"))

    if found is None or data.get("status") != ADJUSTMENT_APPROVED:
        return

    reason, sign = found
    bought = await purchases.for_transaction(data["transaction_id"])

    if bought is None:
        logger.warning("Adjustment %s is for a transaction we didn't sell", data["id"])

        return

    owner_type, owner_id, granted, paid_total = bought

    credits = share(granted, data["totals"]["total"], paid_total)

    if credits:
        await ledger.adjust(
            owner_type, owner_id, sign * credits, f"adjustment:{data['id']}", reason
        )
        await track(
            "credits_taken_back",
            company_id=owner_id,
            why=reason,
            credits=sign * credits,
        )

    if sign < 0 and granted and credits >= granted:
        await take_back_reward(owner_id, data["transaction_id"])
