from app.config.settings import settings
from app.constants.products import CUSTOM_TOP_UP, TOP_UPS


def price_ids() -> dict[str, str]:
    """Paddle's price id of each top-up; one without an id isn't sold."""
    return {product.key: getattr(settings, f"paddle_price_{product.key}") for product in TOP_UPS}


def price_cents_for(price_id: str, quantity: int) -> tuple[str, int] | None:
    """The top-up a Paddle price is (its key) and what it was paid, or None if it isn't ours."""
    if price_id and price_id == settings.paddle_price_topup_custom:
        return CUSTOM_TOP_UP, quantity * 100

    by_price = {price: key for key, price in price_ids().items() if price}
    key = by_price.get(price_id)
    product = next((item for item in TOP_UPS if item.key == key), None)

    return (product.key, product.price_cents * quantity) if product else None
