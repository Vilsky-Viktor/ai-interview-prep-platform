import logging
from datetime import UTC, datetime

from prepza_common.analytics import track

from app.constants.products import OwnerType
from app.helpers.credits import credits_for
from app.helpers.owners import owner_of
from app.services.catalog import price_cents_for
from app.storage import purchases

logger = logging.getLogger(__name__)


async def handle_completed(data: dict) -> None:
    """Adds the credits a completed top-up bought. Whose wallet they go to comes from the
    checkout; the amount comes from Paddle's price id."""
    custom = data.get("custom_data") or {}
    owner_id = custom.get("owner_id")
    owner_type = custom.get("owner_type")

    if not owner_id or owner_type not in tuple(OwnerType):
        logger.warning("Transaction %s has no valid owner", data["id"])

        return

    for item in data.get("items", []):
        quantity = item.get("quantity", 1)
        found = price_cents_for(item["price"]["id"], quantity)

        if found is None:
            logger.warning("Ignoring item %s of transaction %s", item["price"]["id"], data["id"])

            continue

        key, paid_cents = found
        granted = await purchases.grant(
            owner_type,
            owner_id,
            credits_for(paid_cents),
            quantity,
            data["id"],
            key,
            custom.get("buyer_id"),
            data["details"]["totals"]["grand_total"],
            data["currency_code"],
            datetime.now(UTC),
        )

        if granted:
            await track(
                "topped_up",
                **owner_of(owner_type, owner_id),
                amount_cents=paid_cents,
                product=key,
                currency=data["currency_code"],
            )
