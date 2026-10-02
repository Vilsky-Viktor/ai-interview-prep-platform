from dataclasses import dataclass
from enum import StrEnum


class OwnerType(StrEnum):
    COMPANY = "company"
    USER = "user"


@dataclass(frozen=True)
class Product:
    key: str
    title: str
    owner: OwnerType
    # What one purchase grants.
    candidate_credits: int = 0
    generation_credits: int = 0
    pass_days: int = 0
    # Shown before checkout; Paddle charges the price set on its side for the same product.
    price_cents: int = 0


PRODUCTS = [
    Product(
        "candidates_10", "10 candidates", OwnerType.COMPANY, candidate_credits=10, price_cents=5_000
    ),
    Product(
        "candidates_50",
        "50 candidates",
        OwnerType.COMPANY,
        candidate_credits=50,
        price_cents=20_000,
    ),
    Product(
        "candidates_200",
        "200 candidates",
        OwnerType.COMPANY,
        candidate_credits=200,
        price_cents=60_000,
    ),
    Product("job_search_pass", "Job Search Pass", OwnerType.USER, pass_days=90, price_cents=2_400),
    Product(
        "generations_3",
        "3 more preparations",
        OwnerType.USER,
        generation_credits=3,
        price_cents=500,
    ),
]

CURRENCY = "USD"
# Every company starts with this many candidates for free.
FREE_CANDIDATES = 5
# Learners without a pass get this many private preparations a month for free.
FREE_GENERATIONS_PER_MONTH = 1
# Paddle signs each webhook with a timestamp; older ones are refused, so a captured one can't be
# replayed later.
WEBHOOK_TOLERANCE_SECONDS = 5 * 60
# The only Paddle event that grants anything: a fully paid transaction.
TRANSACTION_COMPLETED = "transaction.completed"
DELETED_OWNER = "deleted-user"

NO_CANDIDATE_CREDITS = "No candidate credits left. Buy more to keep inviting candidates."
NO_GENERATIONS = (
    "You've used this month's free preparation. Get the Job Search Pass or 3 more preparations."
)
