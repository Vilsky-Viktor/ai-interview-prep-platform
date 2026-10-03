import time

from fastapi import APIRouter, HTTPException, Query, Request, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.constants import CHAT_FREE_TURNS, REFERRAL_COOKIE
from prepza_common.paging import PageParams

from app.config.settings import settings
from app.constants.credits import (
    CANDIDATE_CREDITS,
    CERTIFICATE_CREDITS,
    CHAT_TURN_CREDITS,
    KIT_CREDITS,
    REFERRAL_MIN_CENTS,
    REFERRAL_REWARD,
    WELCOME_COMPANY,
    WELCOME_USER,
)
from app.constants.products import (
    CURRENCY,
    CUSTOM_MAX_DOLLARS,
    CUSTOM_MIN_DOLLARS,
    TOP_UPS,
    WEBHOOK_TOLERANCE_SECONDS,
    OwnerType,
)
from app.helpers.credits import credits_for
from app.helpers.paddle import signature_valid
from app.helpers.wallets import balance_out, entry_out
from app.schemas.billing import (
    BalanceOut,
    CatalogOut,
    CustomTopUpOut,
    EntryOut,
    QuoteOut,
    ReferralOut,
    TopUpOut,
)
from app.services.catalog import price_ids
from app.services.referrals import referral_out
from app.services.webhooks import handle
from app.storage import ledger, referrals

router = APIRouter(tags=["billing"])


@router.get("/catalog")
def catalog() -> CatalogOut:
    prices = price_ids()

    return CatalogOut(
        environment=settings.paddle_environment,
        client_token=settings.paddle_client_token,
        currency=CURRENCY,
        kit_credits=KIT_CREDITS,
        candidate_credits=CANDIDATE_CREDITS,
        certificate_credits=CERTIFICATE_CREDITS,
        chat_turn_credits=CHAT_TURN_CREDITS,
        chat_free_turns=CHAT_FREE_TURNS,
        welcome_user=WELCOME_USER,
        welcome_company=WELCOME_COMPANY,
        referral_user=REFERRAL_REWARD[OwnerType.USER],
        referral_company=REFERRAL_REWARD[OwnerType.COMPANY],
        referral_company_min_dollars=REFERRAL_MIN_CENTS[OwnerType.COMPANY] // 100,
        products=[
            TopUpOut(
                key=product.key,
                title=product.title,
                price_cents=product.price_cents,
                credits=credits_for(product.price_cents),
                bonus_credits=credits_for(product.price_cents) - product.price_cents,
                price_id=prices[product.key] or None,
            )
            for product in TOP_UPS
        ],
        custom=CustomTopUpOut(
            price_id=settings.paddle_price_topup_custom or None,
            min_dollars=CUSTOM_MIN_DOLLARS,
            max_dollars=CUSTOM_MAX_DOLLARS,
        ),
    )


@router.get("/topups/quote")
def quote(
    dollars: int = Query(ge=CUSTOM_MIN_DOLLARS, le=CUSTOM_MAX_DOLLARS),
) -> QuoteOut:
    """What a custom amount buys, bonus included, so the client shows it without the rule."""
    credits = credits_for(dollars * 100)

    return QuoteOut(
        price_cents=dollars * 100, credits=credits, bonus_credits=credits - dollars * 100
    )


@router.get("/me")
async def my_balance(user: CurrentUser, request: Request) -> BalanceOut:
    # The first visit gives the welcome gift, once per email (the frontend asks on sign-in).
    # A new person who came through a referral link is noted then.
    if await ledger.welcome_user(user.uid, user.email):
        code = request.cookies.get(REFERRAL_COOKIE)
        referred = bool(code) and await referrals.record(code, OwnerType.USER, user.uid, [])
        await track("signed_up", user_id=user.uid, language=user.language, referred=referred)

    return balance_out(await ledger.wallet(OwnerType.USER, user.uid))


@router.get("/me/referral")
async def my_referral(user: CurrentUser) -> ReferralOut:
    return await referral_out(OwnerType.USER, user.uid)


@router.get("/me/history")
async def my_history(user: CurrentUser, page: PageParams) -> list[EntryOut]:
    rows = await ledger.history(OwnerType.USER, user.uid, page.offset, page.limit)

    return [entry_out(row) for row in rows]


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
