# $1 = 100 credits. Amounts are whole credits.
KIT_CREDITS = 500
CANDIDATE_CREDITS = 300
# A certificate on someone else's public kit; its author gets a share of it.
CERTIFICATE_CREDITS = 100
AUTHOR_SHARE_CREDITS = 20
# A tutor turn after the free ones on a question.
CHAT_TURN_CREDITS = 1
WELCOME_USER = 500
WELCOME_COMPANY = 1_500

NOT_ENOUGH = "Not enough credits. Top up to continue."


class Reason:
    """Why credits moved, as the history shows it."""

    WELCOME = "welcome"
    TOPUP = "topup"
    KIT = "kit"
    CANDIDATE = "candidate"
    CERTIFICATE = "certificate"
    AUTHOR_SHARE = "author_share"
    CHAT = "chat"


class GiftKind:
    USER = "user"
    COMPANY = "company"


class HoldStatus:
    OPEN = "open"
    CHARGED = "charged"
    RELEASED = "released"
