# In-app notifications (the header's bell). A service that knows something important happened
# publishes NOTIFICATION_REQUESTED; the notifications service stores it and tells the recipients'
# open tabs at once. Only the kinds below exist, so the bell stays free of noise.
import logging
from enum import StrEnum

from prepza_common import pubsub
from prepza_common.constants import PUBLISH_IN_REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

NOTIFICATION_REQUESTED = "notification.requested"


class NotificationKind(StrEnum):
    # A question in the company's test was flagged, then fixed or replaced by the AI.
    QUESTION_FLAGGED = "question_flagged"
    QUESTION_FIXED = "question_fixed"
    # Someone who came through the owner's referral link topped up.
    REFERRAL_REWARDED = "referral_rewarded"
    # An automatic top-up charged the card, or couldn't.
    AUTO_TOP_UP_CHARGED = "auto_top_up_charged"
    AUTO_TOP_UP_FAILED = "auto_top_up_failed"
    # Companies: a candidate finished, an invite bounced, an interview is ready or was cancelled.
    CANDIDATE_FINISHED = "candidate_finished"
    INVITE_UNDELIVERED = "invite_undelivered"
    INTERVIEW_READY = "interview_ready"
    INTERVIEW_CANCELLED = "interview_cancelled"
    # A superadmin approved or declined the company's verification.
    VERIFICATION_APPROVED = "verification_approved"
    VERIFICATION_DECLINED = "verification_declined"


# Who a notification is for: one user, or every member of a company.
class Recipient(StrEnum):
    USER = "user"
    COMPANY = "company"


def notification(
    recipient: Recipient | str,
    recipient_id: str,
    kind: NotificationKind,
    link: str,
    key: str | None = None,
    **data,
) -> dict:
    """The event's data. `link` is the page it opens; `data` fills its text (titles, emails,
    credits), and must hold nothing a recipient shouldn't see. `key` names what it's about (for
    example an invite), for a handler that may run again on a retried event: the notifications
    service stores one notification per key."""
    event = {
        "recipient": str(recipient),
        "recipient_id": str(recipient_id),
        "kind": str(kind),
        "link": link,
        "data": data,
    }

    if key is not None:
        event["key"] = f"{kind}:{key}"

    return event


async def publish_quietly(event: dict) -> None:
    """For a service without an outbox: a lost notification is better than a failed or slow
    request."""
    try:
        await pubsub.publish(NOTIFICATION_REQUESTED, event, PUBLISH_IN_REQUEST_TIMEOUT_SECONDS)
    except Exception:
        logger.exception("Couldn't publish a %s notification", event["kind"])
