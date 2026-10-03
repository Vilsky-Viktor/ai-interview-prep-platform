from app.constants.products import ADJUSTMENT_EVENTS, TRANSACTION_COMPLETED
from app.services.adjustments import handle_adjustment
from app.services.topups import handle_completed


async def handle(event: dict) -> None:
    """Paddle's events: a paid top-up adds credits; refunds and chargebacks take them back."""
    event_type = event.get("event_type")

    if event_type == TRANSACTION_COMPLETED:
        await handle_completed(event["data"])
    elif event_type in ADJUSTMENT_EVENTS:
        await handle_adjustment(event["data"])
