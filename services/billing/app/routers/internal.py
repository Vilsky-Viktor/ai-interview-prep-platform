from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.constants.products import NO_CANDIDATE_CREDITS, NO_GENERATIONS, OwnerType
from app.schemas.billing import CompanyCreditsOut
from app.service_auth import ServiceCaller
from app.storage import wallets

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/companies/{company_id}/candidates/use", status_code=status.HTTP_204_NO_CONTENT)
async def use_candidate(company_id: str, caller: ServiceCaller) -> None:
    """Called by companies before a new candidate is invited."""
    if not await wallets.use_candidate(company_id):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NO_CANDIDATE_CREDITS)


@router.get("/companies/{company_id}/credits")
async def company_credits(company_id: str, caller: ServiceCaller) -> CompanyCreditsOut:
    return CompanyCreditsOut(candidate_credits=await wallets.company_credits(company_id))


@router.post("/users/{user_id}/generations/use", status_code=status.HTTP_204_NO_CONTENT)
async def use_generation(user_id: str, caller: ServiceCaller) -> None:
    """Called by generation before a learner's preparation is generated."""
    if not await wallets.use_generation(user_id, datetime.now(UTC)):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, NO_GENERATIONS)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, caller: ServiceCaller) -> None:
    """Part of deleting an account (library coordinates it); safe to repeat."""
    await wallets.delete_user(user_id)


@router.get("/users/{user_id}/export")
async def export_user(user_id: str, caller: ServiceCaller) -> dict:
    wallet = await wallets.get(OwnerType.USER, user_id)

    return jsonable_encoder(
        {
            "pass_until": wallet.pass_until if wallet else None,
            "generation_credits": wallet.generation_credits if wallet else 0,
            "purchases": [
                {
                    "product": row.product,
                    "quantity": row.quantity,
                    "total": row.total,
                    "currency": row.currency,
                    "at": row.created_at,
                }
                for row in await wallets.purchases_of(user_id)
            ],
        }
    )
