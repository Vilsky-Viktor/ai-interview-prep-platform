from prepza_common.constants import CREDITS_PER_DOLLAR

from app.constants.credits import CANDIDATE_CREDITS
from app.constants.products import CANDIDATE_PRICE_TIERS

# A candidate's price outside the volume tiers: $5.
BASE_CANDIDATE_CENTS = CANDIDATE_CREDITS * 100 // CREDITS_PER_DOLLAR


def credits_for(price_cents: int) -> int:
    """What a top-up of this amount buys: its candidates at its volume price, in credits; one
    rule for every amount."""
    cents = next(
        (price for floor, price in CANDIDATE_PRICE_TIERS if price_cents >= floor),
        BASE_CANDIDATE_CENTS,
    )

    return price_cents * CANDIDATE_CREDITS // cents


def candidate_prices() -> list[tuple[int, int]]:
    """What a candidate costs in money at each volume tier: (top-up from, in dollars; cents per
    candidate), cheapest last."""
    tiers = sorted(CANDIDATE_PRICE_TIERS)

    return [(1, BASE_CANDIDATE_CENTS)] + [(floor // 100, price) for floor, price in tiers]
