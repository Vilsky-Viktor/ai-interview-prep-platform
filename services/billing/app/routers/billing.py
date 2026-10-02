import time
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.auth import CurrentUser

from app.config.settings import settings
from app.constants.products import (
    CURRENCY,
    FREE_CANDIDATES,
    FREE_GENERATIONS_PER_MONTH,
    PRODUCTS,
    WEBHOOK_TOLERANCE_SECONDS,
    OwnerType,
)
from app.helpers.paddle import signature_valid
from app.schemas.billing import CatalogOut, PlanOut, ProductOut
from app.services.catalog import price_ids
from app.services.webhooks import handle
from app.storage import wallets

router = APIRouter(tags=["billing"])


@router.get("/catalog")
def catalog() -> CatalogOut:
    prices = price_ids()

    return CatalogOut(
        environment=settings.paddle_environment,
        client_token=settings.paddle_client_token,
        currency=CURRENCY,
        free_generations_per_month=FREE_GENERATIONS_PER_MONTH,
        free_candidates=FREE_CANDIDATES,
        products=[
            ProductOut(
                key=product.key,
                title=product.title,
                owner=product.owner,
                price_cents=product.price_cents,
                candidate_credits=product.candidate_credits,
                generation_credits=product.generation_credits,
                pass_days=product.pass_days,
                price_id=prices[product.key] or None,
            )
            for product in PRODUCTS
        ],
    )


@router.get("/me")
async def my_plan(user: CurrentUser) -> PlanOut:
    now = datetime.now(UTC)
    wallet = await wallets.get(OwnerType.USER, user.uid)
    used = await wallets.free_generations_used(user.uid, now)
    active_pass = (
        wallet.pass_until if wallet and wallet.pass_until and wallet.pass_until > now else None
    )

    return PlanOut(
        pass_until=active_pass,
        generation_credits=wallet.generation_credits if wallet else 0,
        free_generations_left=max(0, FREE_GENERATIONS_PER_MONTH - used),
    )


@router.post("/webhooks/paddle", status_code=status.HTTP_200_OK)
async def paddle_webhook(request: Request) -> dict:
    """Paddle retries until it gets a 2xx, and granting is idempotent, so retries are safe."""
    body = await request.body()
    signature = request.headers.get("Paddle-Signature", "")

    if not signature_valid(
        signature, body, settings.paddle_webhook_secret, time.time(), WEBHOOK_TOLERANCE_SECONDS
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

    await handle(await request.json())

    return {"received": True}
