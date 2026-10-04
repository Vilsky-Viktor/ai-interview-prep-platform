# $1 = 100 credits. Amounts are whole credits.
KIT_CREDITS = 800
CANDIDATE_CREDITS = 400
# A certificate on someone else's public kit; its author gets a share of it.
CERTIFICATE_CREDITS = 100
AUTHOR_SHARE_CREDITS = 20
# A tutor turn after the free ones on a question.
CHAT_TURN_CREDITS = 1
# A new learner gets one free kit and 100 credits; a new company its first 3 candidates.
WELCOME_USER = 100
WELCOME_USER_KITS = 1
WELCOME_COMPANY = 1_200
# Below this, a balance is shown as running low, so a learner's chat doesn't stop by surprise
# and a company sees it before it can't invite the next candidate.
LOW_BALANCE = {"user": 100, "company": CANDIDATE_CREDITS}
# Both sides get it once the new learner first tops up any amount, or the new company first
# tops up REFERRAL_MIN_CENTS or more; a referrer is rewarded for at most REFERRALS_PER_YEAR.
REFERRAL_REWARD = {"user": 200, "company": 600}
REFERRAL_MIN_CENTS = {"user": 0, "company": 2_500}
REFERRALS_PER_YEAR = 25
REFERRAL_CODE_BYTES = 6

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
    # Paddle refunded a top-up, or the bank reversed it: the credits it bought go back.
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    # Paddle won a chargeback back: the credits return.
    CHARGEBACK_REVERSED = "chargeback_reversed"
    REFERRAL = "referral"


class GiftKind:
    USER = "user"
    COMPANY = "company"


class HoldStatus:
    OPEN = "open"
    CHARGED = "charged"
    RELEASED = "released"
