import logging
from datetime import UTC, datetime

from app.constants.products import TRANSACTION_COMPLETED
from app.services.catalog import product_for_price
from app.storage import wallets

logger = logging.getLogger(__name__)


async def handle(event: dict) -> None:
    """Grants what a completed transaction bought. The products come from Paddle's price ids,
    never from custom data, which only says whose wallet gets them."""
    if event.get("event_type") != TRANSACTION_COMPLETED:
        return

    data = event["data"]
    custom = data.get("custom_data") or {}
    owner_id = custom.get("owner_id")
    lines = []

    for item in data.get("items", []):
        product = product_for_price(item["price"]["id"])

        if product is None or product.owner != custom.get("owner_type"):
            logger.warning("Ignoring item %s of transaction %s", item["price"]["id"], data["id"])
            continue

        lines.append((product, item.get("quantity", 1)))

    if not owner_id or not lines:
        return

    await wallets.grant(
        data["id"],
        lines,
        owner_id,
        custom.get("buyer_id"),
        data["details"]["totals"]["grand_total"],
        data["currency_code"],
        datetime.now(UTC),
    )
