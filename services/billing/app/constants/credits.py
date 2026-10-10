# $1 = 100 credits. Amounts are whole credits.
CANDIDATE_CREDITS = 300
# A new company gets its first 3 candidates.
WELCOME_COMPANY = 3 * CANDIDATE_CREDITS
# Below this, a balance is shown as running low, so a company sees it before it can't invite the
# next candidate.
LOW_BALANCE = CANDIDATE_CREDITS
# Both sides get it once the new company first tops up, any amount; a referrer is rewarded for at
# most REFERRALS_PER_YEAR.
REFERRAL_REWARD = 500
REFERRALS_PER_YEAR = 25
REFERRAL_CODE_BYTES = 6

NOT_ENOUGH = "Not enough credits. Top up to continue."


class Reason:
    """Why credits moved, as the history shows it."""

    WELCOME = "welcome"
    TOPUP = "topup"
    CANDIDATE = "candidate"
    # Paddle refunded a top-up, or the bank reversed it: the credits it bought go back.
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    # Paddle won a chargeback back: the credits return.
    CHARGEBACK_REVERSED = "chargeback_reversed"
    REFERRAL = "referral"
    # The top-up that paid a referral was refunded in full or charged back: both rewards go back.
    REFERRAL_REVERSED = "referral_reversed"


# Paddle's adjustments of a top-up.
ADJUSTMENTS = (Reason.REFUND, Reason.CHARGEBACK, Reason.CHARGEBACK_REVERSED)

# A candidate's hold and charge are keyed by this and the key companies gives the invite.
CANDIDATE_PREFIX = "candidate:"

# Names the welcome gift (helpers/gifts.py): a person's first company.
WELCOME_GIFT = "company"


class HoldStatus:
    OPEN = "open"
    CHARGED = "charged"
    RELEASED = "released"
