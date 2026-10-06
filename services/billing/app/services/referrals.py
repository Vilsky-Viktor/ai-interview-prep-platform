from prepza_common.analytics import track
from prepza_common.constants import MAX_PAGE_SIZE
from prepza_common.notifications import NotificationKind, notification, publish_quietly

from app.constants.credits import REFERRAL_REWARD
from app.constants.notifications import REFERRAL_LINK
from app.schemas.billing import ReferralOut, ReferralRewardOut
from app.storage import referrals


async def referral_out(owner_type: str, owner_id: str) -> ReferralOut:
    return ReferralOut(
        code=await referrals.code_of(owner_type, owner_id),
        reward=REFERRAL_REWARD,
        rewarded=await referrals.rewarded_count(owner_type, owner_id),
        rewards=[
            ReferralRewardOut(company_id=row.owner_id, rewarded_at=row.rewarded_at)
            for row in await referrals.rewards(owner_type, owner_id, MAX_PAGE_SIZE)
        ],
    )


async def reward_after_top_up(owner_type: str, owner_id: str, transaction_id: str) -> None:
    """The first top-up pays the referral its company came through, once, and tells the
    referrer."""
    referrer_id = await referrals.reward(owner_type, owner_id, transaction_id)

    if referrer_id is not None:
        await track("referral_rewarded", company_id=owner_id)
        await publish_quietly(
            notification(
                owner_type,
                referrer_id,
                NotificationKind.REFERRAL_REWARDED,
                REFERRAL_LINK.format(owner_id=referrer_id),
                credits=REFERRAL_REWARD,
            )
        )


async def take_back_reward(owner_id: str, transaction_id: str) -> None:
    """A top-up refunded in full or charged back no longer pays its referral."""
    if await referrals.take_back(transaction_id):
        await track("referral_reversed", company_id=owner_id)
