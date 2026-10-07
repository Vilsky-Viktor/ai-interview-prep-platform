import logging

from prepza_common import pubsub
from prepza_common.constants import PUBLISH_IN_REQUEST_TIMEOUT_SECONDS

from app.constants.events import CREDITS_ADDED

logger = logging.getLogger(__name__)


async def credits_added(owner_type: str, owner_id: str) -> None:
    """Tells other services the owner got credits, after they're saved. Billing has no outbox: a
    lost event leaves candidates for "Invite again" on the ATS page, better than a failed top-up."""
    try:
        await pubsub.publish(
            CREDITS_ADDED,
            {"owner_type": owner_type, "owner_id": owner_id},
            PUBLISH_IN_REQUEST_TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception("Couldn't publish credits.added for %s", owner_id)
