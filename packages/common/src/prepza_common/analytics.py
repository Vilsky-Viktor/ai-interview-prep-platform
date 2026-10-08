import hashlib
import hmac
import logging
import os
from datetime import UTC, datetime

from prepza_common.constants import FUNNEL_PREFIX, PUBLISH_IN_REQUEST_TIMEOUT_SECONDS
from prepza_common.pubsub import publish

logger = logging.getLogger(__name__)


def pseudonym(user_id: str) -> str:
    """The user as analytics knows them: a salted hash, never the id or email. Once the account
    is deleted, nothing links it back to a person."""
    salt = os.environ.get("ANALYTICS_SALT", "")

    return hmac.new(salt.encode(), user_id.encode(), hashlib.sha256).hexdigest()[:32]


async def track(
    event: str,
    *,
    user_id: str | None = None,
    company_id: object | None = None,
    **props: object,
) -> None:
    """Records one funnel event (internal_docs/measurement.md). Best effort: it waits for Pub/Sub
    only as long as an in-request publish may, and a lost event is logged and never breaks the
    request. `props` hold counts and choices only, never text people wrote."""
    data = {
        "at": datetime.now(UTC).isoformat(),
        "user": pseudonym(user_id) if user_id else None,
        "company": str(company_id) if company_id else None,
        "props": props,
    }

    try:
        await publish(FUNNEL_PREFIX + event, data, PUBLISH_IN_REQUEST_TIMEOUT_SECONDS)
    except Exception:
        logger.warning("Couldn't record funnel event %s", event, exc_info=True)
