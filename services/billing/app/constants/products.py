from dataclasses import dataclass
from enum import StrEnum


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

# $1 buys 100 credits, plus a bonus percent from these amounts up (in cents), largest first.
CREDITS_PER_DOLLAR = 100
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
