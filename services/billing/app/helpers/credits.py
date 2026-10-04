from prepza_common.constants import CREDITS_PER_DOLLAR

from app.constants.products import BONUS_TIERS


def credits_for(price_cents: int) -> int:
    """What a top-up of this amount buys, the bonus included; one rule for every amount."""
    credits = price_cents * CREDITS_PER_DOLLAR // 100
    percent = next((bonus for floor, bonus in BONUS_TIERS if price_cents >= floor), 0)

    return credits + credits * percent // 100
