import base64
import hashlib
import hmac

from prepza_common.notifications import NotificationKind

# Why an ATS candidate wasn't invited, as the message says it.
NOT_INVITED = {
    "credits": "out of credits",
    "limit": "an email limit was reached",
    "paused": "invites are paused",
}


def signed_state(secret: str, company_id: str, user_id: str, expires: int) -> str:
    """The "Add to Slack" trip's state: the company and who started it, until `expires` (Unix
    seconds), signed so the callback can trust it."""
    payload = f"{company_id}|{user_id}|{expires}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode()


def read_state(secret: str, state: str, now: int) -> tuple[str, str] | None:
    """The company and user a state names, if it's ours and not expired."""
    try:
        company_id, user_id, expires, signature = (
            base64.urlsafe_b64decode(state.encode()).decode().split("|")
        )
    except ValueError:
        return None

    payload = f"{company_id}|{user_id}|{expires}"
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected) or int(expires) < now:
        return None

    return company_id, user_id


def message(event: dict, site: str) -> str | None:
    """A notification as a Slack message (in English, like the bell's English text), linking to
    where it points; None for a kind Slack doesn't get."""
    data = event.get("data") or {}
    title = data.get("title") or "an interview"
    texts = {
        NotificationKind.CANDIDATE_FINISHED: f"{data.get('email')} finished “{title}”"
        + (f": {data['grade']}%." if data.get("grade") is not None else "."),
        NotificationKind.ATS_NOT_INVITED: f"{data.get('email')} from {data.get('ats', 'your ATS')}"
        f" wasn't invited to “{title}”: "
        f"{NOT_INVITED.get(data.get('reason'), 'something went wrong')}.",
        NotificationKind.INVITE_UNDELIVERED: f"The invite to {data.get('email')} for “{title}”"
        " wasn't delivered.",
        NotificationKind.INTERVIEW_READY: f"The interview “{title}” is ready.",
        NotificationKind.AUTO_TOP_UP_CHARGED: f"Automatic top-up added {data.get('credits')}"
        " credits.",
        NotificationKind.AUTO_TOP_UP_FAILED: "Automatic top-up couldn't charge the card. Top up"
        " to keep your balance going.",
    }
    text = texts.get(event.get("kind"))

    if text is None:
        return None

    return f"{text} <{site}{event.get('link', '')}|Open in prepza>"
