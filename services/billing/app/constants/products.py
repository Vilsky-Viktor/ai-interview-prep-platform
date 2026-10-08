from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum

from app.constants.credits import CANDIDATE_CREDITS


class OwnerType(StrEnum):
    """Whose wallet; only companies have one."""

    COMPANY = "company"


@dataclass(frozen=True)
class TopUp:
    key: str
    title: str
    price_cents: int


# Fixed amounts; what each buys comes from helpers/credits.py.
# Each buys whole candidates at its volume price: 10 and 50 at $3, 125 at $2, 1,000 at $1.
TOP_UPS = [
    TopUp("topup_30", "$30", 3_000),
    TopUp("topup_150", "$150", 15_000),
    TopUp("topup_250", "$250", 25_000),
    TopUp("topup_1000", "$1,000", 100_000),
]

# $1 buys CREDITS_PER_DOLLAR credits, plus a bonus percent from these amounts up (in cents),
# largest first: volume prices, so a candidate (CANDIDATE_CREDITS) costs $3, $2 when bought in a
# top-up from $250, and $1 from $1,000.
BONUS_TIERS = [(100_000, 200), (25_000, 50)]

CURRENCY = "USD"
# Paddle signs each webhook with a timestamp; older ones are refused, so a captured one can't be
# replayed later.
WEBHOOK_TOLERANCE_SECONDS = 5 * 60
# The only Paddle event that grants anything: a fully paid transaction.
TRANSACTION_COMPLETED = "transaction.completed"
# Refunds and chargebacks; a refund is approved after it's created, so both events matter.
ADJUSTMENT_EVENTS = ("adjustment.created", "adjustment.updated")
ADJUSTMENT_APPROVED = "approved"

# Automatic top-up: the balances (in credits) it can refill under, and the least time between two
# automatic charges, so a webhook still on its way can't cause a second one.
# They cover 1, 3 and 5 candidates.
AUTO_TOP_UP_THRESHOLDS = [CANDIDATE_CREDITS, 3 * CANDIDATE_CREDITS, 5 * CANDIDATE_CREDITS]
AUTO_TOP_UP_COOLDOWN = timedelta(minutes=10)
# After the card declines a charge, the next try (and its notice to the owner) waits this long,
# unless the automatic top-up is saved again first (say, after updating the card).
AUTO_TOP_UP_RETRY_AFTER = timedelta(days=1)
# Turning it on is a checkout for a $0 monthly subscription, which saves the card; Paddle tells
# us when it starts and when it ends (cancelled in Paddle, or after failed payments).
SUBSCRIPTION_CREATED = "subscription.created"
SUBSCRIPTION_CANCELED = "subscription.canceled"
# A subscription's status in Paddle once it has ended.
SUBSCRIPTION_ENDED_STATUS = "canceled"
# Marks the checkout that turns automatic top-up on.
AUTO_TOP_UP_FLAG = "auto_top_up"
PADDLE_API = {"sandbox": "https://sandbox-api.paddle.com", "production": "https://api.paddle.com"}
