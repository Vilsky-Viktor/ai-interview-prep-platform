import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from prepza_common.analytics import track
from prepza_common.notifications import NotificationKind, notification, publish_quietly

from app.config.settings import settings
from app.constants.notifications import TOP_UP_LINK
from app.constants.products import AUTO_TOP_UP_FLAG, AUTO_TOP_UP_THRESHOLDS
from app.integrations import paddle
from app.schemas.billing import AutoTopUpIn, AutoTopUpOut, CheckoutOut
from app.services.catalog import price_ids
from app.storage import auto_top_ups

logger = logging.getLogger(__name__)


def offered() -> bool:
    return bool(settings.paddle_api_key and settings.paddle_price_auto_top_up)


def products() -> list[str]:
    """The top-ups it can buy: the fixed ones on sale."""
    return [key for key, price in price_ids().items() if price]


async def out(owner_type: str, owner_id: str) -> AutoTopUpOut:
    row = await auto_top_ups.get(owner_type, owner_id)
    started = row is not None and row.subscription_id is not None

    return AutoTopUpOut(
        offered=offered(),
        on=started,
        waiting=row is not None and not started,
        product=row.product if row else None,
        threshold=row.threshold if row else None,
        products=products(),
        thresholds=AUTO_TOP_UP_THRESHOLDS,
    )


async def turn_on(owner_type: str, owner_id: str, body: AutoTopUpIn, buyer_id: str) -> AutoTopUpOut:
    """Saves the choice. If it isn't running yet, the answer carries the checkout that saves
    the card; it starts when Paddle confirms the subscription."""
    if not offered() or body.product not in products():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "This top-up isn't available")

    if body.threshold not in AUTO_TOP_UP_THRESHOLDS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Choose one of the balances")

    row = await auto_top_ups.save(owner_type, owner_id, body.product, body.threshold, buyer_id)
    result = await out(owner_type, owner_id)

    if row.subscription_id is None:
        result.checkout = CheckoutOut(
            price_id=settings.paddle_price_auto_top_up,
            custom_data={
                "owner_type": owner_type,
                "owner_id": owner_id,
                "buyer_id": buyer_id,
                AUTO_TOP_UP_FLAG: "1",
            },
        )

    return result


async def turn_off(owner_type: str, owner_id: str) -> None:
    """Off at once; the subscription that kept the card is cancelled."""
    subscription_id = await auto_top_ups.remove(owner_type, owner_id)

    if subscription_id:
        await cancel_quietly(subscription_id)


async def forget_buyer(buyer_id: str) -> None:
    """A deleted account's card is never charged again: its automatic top-ups go off."""
    for subscription_id in await auto_top_ups.remove_for_buyer(buyer_id):
        await cancel_quietly(subscription_id)


async def cancel_quietly(subscription_id: str) -> None:
    try:
        await paddle.cancel(subscription_id)
    except Exception:
        logger.exception("Couldn't cancel subscription %s", subscription_id)


async def start(custom: dict, subscription_id: str) -> None:
    """Paddle confirmed the checkout's subscription. One nobody is waiting for (turned off
    meanwhile, or not started by whoever turned it on) is cancelled, so no card is kept."""
    if custom.get(AUTO_TOP_UP_FLAG) != "1":
        return

    owner = (custom.get("owner_type"), custom.get("owner_id"))

    if await auto_top_ups.owner_of(subscription_id) == owner:
        return

    if not await auto_top_ups.start(*owner, custom.get("buyer_id"), subscription_id):
        await cancel_quietly(subscription_id)

        return

    await track("auto_top_up_on", company_id=owner[1])
    # The balance may already be under the threshold.
    await check(*owner)


async def owner(subscription_id: str) -> tuple[str, str] | None:
    """Whose wallet an automatic charge on this subscription is for."""
    return await auto_top_ups.owner_of(subscription_id)


async def ended(subscription_id: str) -> None:
    """Paddle ended the subscription (cancelled there, or after failed payments): it's off."""
    await auto_top_ups.remove_subscription(subscription_id)


async def check(owner_type: str, owner_id: str) -> None:
    """After credits are used: if the balance is now under the threshold, buys the chosen
    top-up with the saved card. Never fails the request that used the credits; a charge that
    fails (a declined card) is told to the owner."""
    row = None

    try:
        row = await auto_top_ups.claim_charge(owner_type, owner_id, datetime.now(UTC))

        if row is None:
            return

        await paddle.charge(row.subscription_id, price_ids()[row.product])
    except Exception:
        logger.exception("Automatic top-up failed for %s %s", owner_type, owner_id)

        if row is not None:
            await publish_quietly(
                notification(owner_type, owner_id, NotificationKind.AUTO_TOP_UP_FAILED, TOP_UP_LINK)
            )
