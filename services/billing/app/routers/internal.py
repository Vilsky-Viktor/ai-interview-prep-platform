from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from prepza_common.paging import PageParams

from app.constants.credits import (
    AUTHOR_SHARE_CREDITS,
    CANDIDATE_CREDITS,
    CERTIFICATE_CREDITS,
    CHAT_TURN_CREDITS,
    KIT_CREDITS,
    NOT_ENOUGH,
    Reason,
)
from app.constants.products import OwnerType
from app.helpers.wallets import balance_out, entry_out
from app.schemas.billing import BalanceOut, EntryOut, OwnersIn, SpendIn, WelcomeIn
from app.service_auth import ServiceCaller
from app.storage import ledger, purchases

router = APIRouter(prefix="/internal", tags=["internal"])


async def take(owner_type: str, owner_id: str, amount: int, key: str, reason: str) -> None:
    if not await ledger.reserve(owner_type, owner_id, amount, key, reason):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH)


@router.post("/kits/{generation_id}/hold", status_code=status.HTTP_204_NO_CONTENT)
async def hold_kit(generation_id: str, user_id: str, caller: ServiceCaller) -> None:
    """A learner's prep kit. Charged when it's ready, given back if it fails or is cancelled."""
    await take(OwnerType.USER, user_id, KIT_CREDITS, f"kit:{generation_id}", Reason.KIT)


@router.post("/kits/{generation_id}/charge", status_code=status.HTTP_204_NO_CONTENT)
async def charge_kit(generation_id: str, caller: ServiceCaller) -> None:
    await ledger.charge(f"kit:{generation_id}")


@router.post("/kits/{generation_id}/release", status_code=status.HTTP_204_NO_CONTENT)
async def release_kit(generation_id: str, caller: ServiceCaller) -> None:
    await ledger.release(f"kit:{generation_id}")


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


@router.post("/certificates", status_code=status.HTTP_204_NO_CONTENT)
async def charge_certificate(body: SpendIn, caller: ServiceCaller) -> None:
    """A certificate on someone else's public kit; its author gets a share."""
    share = (body.author_id, AUTHOR_SHARE_CREDITS) if body.author_id else None

    if not await ledger.spend(
        OwnerType.USER,
        body.owner_id,
        CERTIFICATE_CREDITS,
        f"certificate:{body.key}",
        Reason.CERTIFICATE,
        body.note,
        share,
    ):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH)


@router.post("/chat-turns", status_code=status.HTTP_204_NO_CONTENT)
async def charge_chat_turn(body: SpendIn, caller: ServiceCaller) -> None:
    """A tutor turn after the free ones on a question."""
    if not await ledger.spend(
        OwnerType.USER, body.owner_id, CHAT_TURN_CREDITS, f"chat:{body.key}", Reason.CHAT
    ):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NOT_ENOUGH)


@router.get("/users/{user_id}/credits")
async def user_credits(user_id: str, caller: ServiceCaller) -> BalanceOut:
    """For a check before work starts, such as a chat turn."""
    return balance_out(await ledger.wallet(OwnerType.USER, user_id))


@router.post("/companies/{company_id}/welcome", status_code=status.HTTP_204_NO_CONTENT)
async def welcome_company(company_id: str, body: WelcomeIn, caller: ServiceCaller) -> None:
    """The company's wallet. The welcome credits come once per owner's email."""
    await ledger.welcome_company(company_id, body.owner_email)


@router.get("/companies/{company_id}/credits")
async def company_credits(company_id: str, caller: ServiceCaller) -> BalanceOut:
    return balance_out(await ledger.wallet(OwnerType.COMPANY, company_id))


@router.post("/companies/credits")
async def companies_credits(body: OwnersIn, caller: ServiceCaller) -> dict[str, BalanceOut]:
    """Several companies' balances at once, for the top-up page."""
    found = await ledger.wallets(OwnerType.COMPANY, body.owner_ids)
    empty = BalanceOut(balance=0, reserved=0, available=0)

    return {
        owner_id: balance_out(found[owner_id]) if owner_id in found else empty
        for owner_id in body.owner_ids
    }


@router.get("/companies/{company_id}/history")
async def company_history(
    company_id: str, caller: ServiceCaller, page: PageParams
) -> list[EntryOut]:
    rows = await ledger.history(OwnerType.COMPANY, company_id, page.offset, page.limit)

    return [entry_out(row) for row in rows]


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, caller: ServiceCaller) -> None:
    await purchases.delete_company(company_id)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, caller: ServiceCaller) -> None:
    await purchases.delete_user(user_id)


@router.get("/users/{user_id}/export")
async def export_user(user_id: str, caller: ServiceCaller) -> dict:
    row = await ledger.wallet(OwnerType.USER, user_id)
    history = await ledger.history(OwnerType.USER, user_id, 0, 10_000)

    return jsonable_encoder(
        {
            "balance": row.balance,
            "reserved": row.reserved,
            "history": [entry_out(item).model_dump() for item in history],
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
