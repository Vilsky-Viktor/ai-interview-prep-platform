from prepza_common.analytics import track
from prepza_common.notifications import NotificationKind, notification, publish_quietly

from app.constants.credits import REFERRAL_MIN_CENTS, REFERRAL_REWARD
from app.constants.notifications import REFERRAL_LINKS
from app.helpers.owners import owner_of
from app.schemas.billing import ReferralOut
from app.storage import referrals


async def referral_out(owner_type: str, owner_id: str) -> ReferralOut:
    return ReferralOut(
        code=await referrals.code_of(owner_type, owner_id),
        reward=REFERRAL_REWARD[owner_type],
        min_dollars=REFERRAL_MIN_CENTS[owner_type] // 100,
        rewarded=await referrals.rewarded_count(owner_type, owner_id),
    )


async def reward_after_top_up(owner_type: str, owner_id: str, paid_cents: int) -> None:
    """A top-up big enough pays the referral its owner came through, once, and tells the
    referrer (who has the same owner type)."""
    if paid_cents < REFERRAL_MIN_CENTS[owner_type]:
        return

    referrer_id = await referrals.reward(owner_type, owner_id)

    if referrer_id is not None:
        await track("referral_rewarded", **owner_of(owner_type, owner_id))
        await publish_quietly(
            notification(
                owner_type,
                referrer_id,
                NotificationKind.REFERRAL_REWARDED,
                REFERRAL_LINKS[owner_type].format(owner_id=referrer_id),
                credits=REFERRAL_REWARD[owner_type],
            )
        )
