from app.config.settings import settings
from app.constants.products import PRODUCTS, Product


def price_ids() -> dict[str, str]:
    """Paddle's price id of each product key; products without one aren't sold."""
    return {product.key: getattr(settings, f"paddle_price_{product.key}") for product in PRODUCTS}


def product_for_price(price_id: str) -> Product | None:
    by_price = {price: key for key, price in price_ids().items() if price}
    key = by_price.get(price_id)

    return next((product for product in PRODUCTS if product.key == key), None)
