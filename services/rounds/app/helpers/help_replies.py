import hashlib
import hmac

from prepza_common.tokens import same_secret

from app.constants.help import HelpRole
from app.schemas.help import HelpMessage


def reply_signature(content: str, secret: str) -> str:
    """The signature the help chat gives a reply it wrote: the page sends it back with the reply,
    so a reply the page made up can't steer the next answer."""
    return hmac.new(secret.encode(), b"help-reply:" + content.encode(), hashlib.sha256).hexdigest()


def trusted(messages: list[HelpMessage], secret: str) -> list[HelpMessage]:
    """The conversation as the model may read it: every question, and only the replies the help
    chat signed itself."""
    return [
        message
        for message in messages
        if message.role == HelpRole.USER
        or same_secret(message.signature or "", reply_signature(message.content, secret))
    ]
