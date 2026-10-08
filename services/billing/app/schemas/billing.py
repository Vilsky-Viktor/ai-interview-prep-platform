from datetime import datetime

from prepza_common.constants import MAX_PAGE_SIZE
from pydantic import BaseModel, Field


class TopUpOut(BaseModel):
    key: str
    title: str
    price_cents: int
    credits: int
    # The whole candidates it buys, and what each costs at its volume price.
    candidates: int
    candidate_cents: int
    price_id: str | None


class CandidatePriceOut(BaseModel):
    """A candidate's price when credits are bought in a top-up from this many dollars."""

    from_dollars: int
    cents: int


class CatalogOut(BaseModel):
    """What the pricing page and Paddle.js need. Prices are decided here, not in the client."""

    environment: str
    client_token: str
    currency: str
    candidate_credits: int
    # A candidate's price at each volume tier, cheapest last.
    candidate_prices: list[CandidatePriceOut]
    # The cheapest and the standard price of a candidate, for "$1–3 per candidate".
    candidate_cents_min: int
    candidate_cents_max: int
    welcome_company: int
    # The candidates a new company's welcome credits cover.
    free_candidates: int
    referral_company: int
    products: list[TopUpOut]


class BalanceOut(BaseModel):
    balance: int
    reserved: int
    available: int
    # Running low: time to suggest a top-up.
    low: bool


class OwnersIn(BaseModel):
    owner_ids: list[str] = Field(max_length=MAX_PAGE_SIZE)


class WelcomeIn(BaseModel):
    owner_email: str
    # The code of the link the owner came through, and their other companies, which can't
    # refer this one.
    referral: str | None = None
    related: list[str] = Field(default=[], max_length=MAX_PAGE_SIZE)


class ReferralRewardOut(BaseModel):
    """A company that came through the link and topped up, so both got the reward."""

    company_id: str
    rewarded_at: datetime


class ReferralOut(BaseModel):
    """The owner's referral link code, what it earns, and how many it has earned for."""

    code: str
    reward: int
    rewarded: int
    # The latest rewards, newest first.
    rewards: list[ReferralRewardOut]


class AutoTopUpIn(BaseModel):
    """Which top-up to buy, and under which available balance (credits)."""

    product: str
    threshold: int


class CheckoutOut(BaseModel):
    """The Paddle checkout to open: its price and the custom data to send with it."""

    price_id: str
    custom_data: dict[str, str]


class AutoTopUpOut(BaseModel):
    """A wallet's automatic top-up: whether it's offered at all, running, or waiting for its
    checkout, what it buys and when, and the choices."""

    offered: bool
    on: bool
    waiting: bool
    product: str | None
    threshold: int | None
    products: list[str]
    thresholds: list[int]
    # Only when turning it on still needs the checkout that saves the card.
    checkout: CheckoutOut | None = None
