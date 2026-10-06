import logging
from datetime import UTC, datetime

from prepza_common.analytics import track
from prepza_common.notifications import NotificationKind, notification, publish_quietly

from app.config.settings import settings
from app.constants.notifications import TOP_UP_LINK
from app.constants.products import OwnerType
from app.helpers.credits import credits_for
from app.services import auto_top_ups
from app.services.catalog import price_cents_for
from app.services.referrals import reward_after_top_up
from app.storage import purchases

logger = logging.getLogger(__name__)


async def handle_completed(data: dict) -> None:
    """Adds the credits a completed top-up bought. Whose wallet they go to comes from the
    checkout, or for an automatic top-up from its subscription; the amount comes from Paddle's
    price id."""
    custom = data.get("custom_data") or {}
    owner_id = custom.get("owner_id")
    owner_type = custom.get("owner_type")
    subscription_id = data.get("subscription_id")

    if subscription_id:
        # The checkout that turns automatic top-up on; its $0 price buys nothing.
        await auto_top_ups.start(custom, subscription_id)
        owner_type, owner_id = await auto_top_ups.owner(subscription_id) or (
            owner_type,
            owner_id,
        )

    if not owner_id or owner_type not in tuple(OwnerType):
        logger.warning("Transaction %s has no valid owner", data["id"])

        return

    for item in data.get("items", []):
        if item["price"]["id"] == settings.paddle_price_auto_top_up:
            continue

        quantity = item.get("quantity", 1)
        found = price_cents_for(item["price"]["id"], quantity)

        if found is None:
            logger.warning("Ignoring item %s of transaction %s", item["price"]["id"], data["id"])

            continue

        key, paid_cents = found
        credits = credits_for(paid_cents)
        granted = await purchases.grant(
            owner_type,
            owner_id,
            credits,
            quantity,
            data["id"],
            key,
            custom.get("buyer_id"),
            data["details"]["totals"]["grand_total"],
            data["currency_code"],
            datetime.now(UTC),
        )

        # Paid once (it's idempotent), also on Paddle's retry after a failure right after the
        # grant, so the referral is never lost.
        await reward_after_top_up(owner_type, owner_id)

        if granted:
            await track(
                "topped_up",
                company_id=owner_id,
                amount_cents=paid_cents,
                product=key,
                currency=data["currency_code"],
                automatic=subscription_id is not None,
            )

            if subscription_id:
                await publish_quietly(
                    notification(
                        owner_type,
                        owner_id,
                        NotificationKind.AUTO_TOP_UP_CHARGED,
                        TOP_UP_LINK,
                        credits=credits,
                    )
                )
