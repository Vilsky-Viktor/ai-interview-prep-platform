from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum

from app.constants.credits import CANDIDATE_CREDITS, KIT_CREDITS


class OwnerType(StrEnum):
    COMPANY = "company"
    USER = "user"


@dataclass(frozen=True)
class TopUp:
    key: str
    title: str
    price_cents: int


# Fixed amounts; what each buys comes from helpers/credits.py.
TOP_UPS = [
    TopUp("topup_10", "$10", 1_000),
    TopUp("topup_25", "$25", 2_500),
    TopUp("topup_50", "$50", 5_000),
    TopUp("topup_100", "$100", 10_000),
    TopUp("topup_250", "$250", 25_000),
    TopUp("topup_500", "$500", 50_000),
]

# A top-up of any whole-dollar amount in this range: Paddle's $1 price bought in that quantity.
CUSTOM_TOP_UP = "topup_custom"
CUSTOM_MIN_DOLLARS = 10
CUSTOM_MAX_DOLLARS = 500

# $1 buys CREDITS_PER_DOLLAR credits, plus a bonus percent from these amounts up (in cents),
# largest first.
BONUS_TIERS = [(50_000, 10), (25_000, 5), (10_000, 2)]

CURRENCY = "USD"
# Paddle signs each webhook with a timestamp; older ones are refused, so a captured one can't be
# replayed later.
WEBHOOK_TOLERANCE_SECONDS = 5 * 60
# The only Paddle event that grants anything: a fully paid transaction.
TRANSACTION_COMPLETED = "transaction.completed"
# Refunds and chargebacks; a refund is approved after it's created, so both events matter.
ADJUSTMENT_EVENTS = ("adjustment.created", "adjustment.updated")
ADJUSTMENT_APPROVED = "approved"
DELETED_OWNER = "deleted-user"

# Automatic top-up: the balances (in credits) it can refill under, and the least time between two
# automatic charges, so a webhook still on its way can't cause a second one.
# A learner's top one is a kit; a company's cover 1, 3 and 5 candidates.
AUTO_TOP_UP_THRESHOLDS = {
    "user": [100, 300, KIT_CREDITS],
    "company": [CANDIDATE_CREDITS, 3 * CANDIDATE_CREDITS, 5 * CANDIDATE_CREDITS],
}
AUTO_TOP_UP_COOLDOWN = timedelta(minutes=10)
# Turning it on is a checkout for a $0 monthly subscription, which saves the card; Paddle tells
# us when it starts and when it ends (cancelled in Paddle, or after failed payments).
SUBSCRIPTION_CREATED = "subscription.created"
SUBSCRIPTION_CANCELED = "subscription.canceled"
# Marks the checkout that turns automatic top-up on.
AUTO_TOP_UP_FLAG = "auto_top_up"
PADDLE_API = {"sandbox": "https://sandbox-api.paddle.com", "production": "https://api.paddle.com"}
