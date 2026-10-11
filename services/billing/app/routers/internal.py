from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.encoders import jsonable_encoder
from prepza_common.analytics import track
from prepza_common.paging import PageParams

from app.constants.credits import CANDIDATE_CREDITS, CANDIDATE_PREFIX, NOT_ENOUGH, Reason
from app.constants.products import OwnerType
from app.helpers.history import history_entry_out
from app.helpers.wallets import balance_out
from app.integrations import paddle
from app.schemas.billing import (
    BalanceOut,
    HistoryEntryOut,
    InvoiceOut,
    LowCompaniesOut,
    LowCompanyOut,
    OwnersIn,
    PaidOut,
    ReferralOut,
    WelcomeIn,
)
from app.service_auth import ServiceCaller
from app.services import auto_top_ups
from app.services.referrals import referral_out
from app.storage import history, ledger, purchases, referrals

router = APIRouter(prefix="/internal", tags=["internal"])


async def refuse(owner_type: str, owner_id: str, reason: str) -> None:
    await track("balance_too_low", company_id=owner_id, what=reason)
    # An automatic top-up refills it for the next try.
    await auto_top_ups.check(owner_type, owner_id)

    raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH)


@router.post("/candidates/hold", status_code=status.HTTP_204_NO_CONTENT)
async def hold_candidate(
    company_id: str, key: str, caller: ServiceCaller, background: BackgroundTasks
) -> None:
    """Set aside on invite. Charged once the interview finishes with at least one answer. An
    automatic top-up the balance now calls for is charged after answering: Paddle can take its
    time, and the invite waiting on this answer mustn't."""
    held = await ledger.reserve(
        OwnerType.COMPANY, company_id, CANDIDATE_CREDITS, CANDIDATE_PREFIX + key, Reason.CANDIDATE
    )

    if not held:
        await refuse(OwnerType.COMPANY, company_id, Reason.CANDIDATE)

    background.add_task(auto_top_ups.check, OwnerType.COMPANY, company_id)


@router.post("/candidates/charge", status_code=status.HTTP_204_NO_CONTENT)
async def charge_candidate(key: str, caller: ServiceCaller) -> None:
    await ledger.charge(CANDIDATE_PREFIX + key)


@router.post("/candidates/release", status_code=status.HTTP_204_NO_CONTENT)
async def release_candidate(key: str, caller: ServiceCaller) -> None:
    await ledger.release(CANDIDATE_PREFIX + key)


@router.post("/companies/{company_id}/welcome", status_code=status.HTTP_204_NO_CONTENT)
async def welcome_company(company_id: str, body: WelcomeIn, caller: ServiceCaller) -> None:
    """The company's wallet. The welcome credits come once per owner's email; a company new
    in that sense can be referred by another, unrelated one."""
    if await ledger.welcome_company(company_id, body.owner_email) and body.referral:
        await referrals.record(body.referral, OwnerType.COMPANY, company_id, body.related)


@router.get("/companies/{company_id}/paid")
async def company_paid(company_id: str, caller: ServiceCaller) -> PaidOut:
    return PaidOut(paid=await purchases.paid(OwnerType.COMPANY, company_id))


@router.get("/companies/{company_id}/referral")
async def company_referral(company_id: str, caller: ServiceCaller) -> ReferralOut:
    return await referral_out(OwnerType.COMPANY, company_id)


@router.get("/companies/{company_id}/credits")
async def company_credits(company_id: str, caller: ServiceCaller) -> BalanceOut:
    return balance_out(await ledger.wallet(OwnerType.COMPANY, company_id))


@router.get("/companies/{company_id}/history")
async def company_history(
    company_id: str, page: PageParams, caller: ServiceCaller
) -> list[HistoryEntryOut]:
    """Every movement of the company's credits, newest first."""
    rows = await history.page(OwnerType.COMPANY, company_id, page.offset, page.limit)

    return [history_entry_out(row) for row in rows]


@router.get("/companies/{company_id}/invoice")
async def company_invoice(
    company_id: str, transaction_id: str, caller: ServiceCaller
) -> InvoiceOut:
    """The invoice of one of the company's top-ups; 404 for anyone else's transaction."""
    if not await purchases.owns(OwnerType.COMPANY, company_id, transaction_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    return InvoiceOut(url=await paddle.invoice_url(transaction_id))


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
