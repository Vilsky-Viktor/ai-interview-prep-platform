from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from prepza_common.analytics import track

from app.constants.credits import CANDIDATE_CREDITS, NOT_ENOUGH, Reason
from app.constants.products import OwnerType
from app.helpers.wallets import balance_out
from app.schemas.billing import (
    BalanceOut,
    LowCompaniesOut,
    LowCompanyOut,
    OwnersIn,
    ReferralOut,
    WelcomeIn,
)
from app.service_auth import ServiceCaller
from app.services import auto_top_ups
from app.services.referrals import referral_out
from app.storage import ledger, purchases, referrals

router = APIRouter(prefix="/internal", tags=["internal"])


async def refuse(owner_type: str, owner_id: str, reason: str) -> None:
    await track("balance_too_low", company_id=owner_id, what=reason)
    # An automatic top-up refills it for the next try.
    await auto_top_ups.check(owner_type, owner_id)

    raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH)


async def take(owner_type: str, owner_id: str, amount: int, key: str, reason: str) -> None:
    if not await ledger.reserve(owner_type, owner_id, amount, key, reason):
        await refuse(owner_type, owner_id, reason)

    await auto_top_ups.check(owner_type, owner_id)


@router.post("/candidates/hold", status_code=status.HTTP_204_NO_CONTENT)
async def hold_candidate(company_id: str, key: str, caller: ServiceCaller) -> None:
    """Set aside on invite. Charged once the interview finishes with at least one answer."""
    await take(
        OwnerType.COMPANY, company_id, CANDIDATE_CREDITS, f"candidate:{key}", Reason.CANDIDATE
    )


@router.post("/candidates/charge", status_code=status.HTTP_204_NO_CONTENT)
async def charge_candidate(key: str, caller: ServiceCaller) -> None:
    await ledger.charge(f"candidate:{key}")


@router.post("/candidates/release", status_code=status.HTTP_204_NO_CONTENT)
async def release_candidate(key: str, caller: ServiceCaller) -> None:
    await ledger.release(f"candidate:{key}")


@router.post("/companies/{company_id}/welcome", status_code=status.HTTP_204_NO_CONTENT)
async def welcome_company(company_id: str, body: WelcomeIn, caller: ServiceCaller) -> None:
    """The company's wallet. The welcome credits come once per owner's email; a company new
    in that sense can be referred by another, unrelated one."""
    if await ledger.welcome_company(company_id, body.owner_email) and body.referral:
        await referrals.record(body.referral, OwnerType.COMPANY, company_id, body.related)


@router.get("/companies/{company_id}/referral")
async def company_referral(company_id: str, caller: ServiceCaller) -> ReferralOut:
    return await referral_out(OwnerType.COMPANY, company_id)


@router.get("/companies/{company_id}/credits")
async def company_credits(company_id: str, caller: ServiceCaller) -> BalanceOut:
    return balance_out(await ledger.wallet(OwnerType.COMPANY, company_id))


@router.post("/companies/credits")
async def companies_credits(body: OwnersIn, caller: ServiceCaller) -> dict[str, BalanceOut]:
    """Several companies' balances at once, for the top-up page."""
    found = await ledger.wallets(OwnerType.COMPANY, body.owner_ids)
    empty = BalanceOut(balance=0, reserved=0, available=0, low=True, candidates=0)

    return {
        owner_id: balance_out(found[owner_id]) if owner_id in found else empty
        for owner_id in body.owner_ids
    }


@router.get("/companies/low")
async def low_companies(caller: ServiceCaller) -> LowCompaniesOut:
    """Notifications, for its reminders: companies running low on credits that no automatic
    top-up refills."""
    return LowCompaniesOut(
        companies=[
            LowCompanyOut(company_id=row.owner_id, available=row.balance - row.reserved)
            for row in await ledger.running_low(OwnerType.COMPANY)
        ]
    )


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, caller: ServiceCaller) -> None:
    await auto_top_ups.turn_off(OwnerType.COMPANY, company_id)
    await purchases.delete_company(company_id)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, caller: ServiceCaller) -> None:
    """The user's purchases for their companies stay for bookkeeping, without their id; any
    automatic top-up paid with their card goes off."""
    await auto_top_ups.forget_buyer(user_id)
    await purchases.forget_buyer(user_id)


@router.post("/users/{user_id}/export")
async def export_user(user_id: str, caller: ServiceCaller) -> dict:
    """What the user bought for their companies."""
    return jsonable_encoder(
        {
            "purchases": [
                {
                    "product": item.product,
                    "quantity": item.quantity,
                    "total": item.total,
                    "currency": item.currency,
                    "at": item.created_at,
                }
                for item in await purchases.purchases_of(user_id)
            ],
        }
    )
