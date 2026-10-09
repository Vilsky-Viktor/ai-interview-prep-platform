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


def escaped(text: str) -> str:
    """`text` as Slack shows it, never as markup: a title "<!channel>" doesn't ping anyone."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def signed_state(secret: str, company_id: str, user_id: str, expires: int, nonce: str) -> str:
    """The "Add to Slack" trip's state: the company and who started it, until `expires` (Unix
    seconds), signed so the callback can trust it; `nonce` lets the callback take it once."""
    payload = f"{company_id}|{user_id}|{expires}|{nonce}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode()


def read_state(secret: str, state: str, now: int) -> tuple[str, str, str] | None:
    """The company, user and nonce a state names, if it's ours and not expired."""
    try:
        company_id, user_id, expires, nonce, signature = (
            base64.urlsafe_b64decode(state.encode()).decode().split("|")
        )
    except ValueError:
        return None

    payload = f"{company_id}|{user_id}|{expires}|{nonce}"
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected) or int(expires) < now:
        return None

    return company_id, user_id, nonce


def message(event: dict, site: str) -> str | None:
    """A notification as a Slack message (in English, like the bell's English text), linking to
    where it points; None for a kind Slack doesn't get."""
    data = event.get("data") or {}
    title = data.get("title") or "an interview"
    # "Name (email)" once the candidate's name is known.
    candidate = (
        f"{data['candidate_name']} ({data.get('email')})"
        if data.get("candidate_name")
        else data.get("email")
    )
    texts = {
        NotificationKind.CANDIDATE_FINISHED: f"{candidate} finished “{title}”"
        + (f": {data['grade']}%." if data.get("grade") is not None else "."),
        NotificationKind.ATS_NOT_INVITED: f"{candidate} from {data.get('ats', 'your ATS')}"
        f" wasn't invited to “{title}”: "
        f"{NOT_INVITED.get(data.get('reason'), 'something went wrong')}.",
        NotificationKind.INVITE_UNDELIVERED: f"The invite to {candidate} for “{title}”"
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

    # Only the values people wrote are escaped: the link is ours.
    return f"{escaped(text)} <{site}{event.get('link', '')}|Open in prepza>"
