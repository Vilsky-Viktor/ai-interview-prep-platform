from datetime import datetime

from prepza_common.constants import MAX_PAGE_SIZE
from pydantic import BaseModel, Field


class TopUpOut(BaseModel):
    key: str
    title: str
    price_cents: int
    credits: int
    # Credits above the plain rate of 100 per dollar: the bonus on large top-ups.
    bonus_credits: int
    price_id: str | None


class CustomTopUpOut(BaseModel):
    """Any whole-dollar amount in the range: Paddle's $1 price in that quantity."""

    price_id: str | None
    min_dollars: int
    max_dollars: int


class QuoteOut(BaseModel):
    """What a custom amount buys."""

    price_cents: int
    credits: int
    bonus_credits: int


class CatalogOut(BaseModel):
    """What the pricing page and Paddle.js need. Prices are decided here, not in the client."""

    environment: str
    client_token: str
    currency: str
    kit_credits: int
    candidate_credits: int
    certificate_credits: int
    chat_turn_credits: int
    chat_free_turns: int
    welcome_user: int
    welcome_company: int
    # How many topics a free kit (the learner's welcome gift) has.
    free_kit_topics: int
    referral_user: int
    referral_company: int
    referral_company_min_dollars: int
    products: list[TopUpOut]
    custom: CustomTopUpOut


class BalanceOut(BaseModel):
    balance: int
    reserved: int
    available: int
    # Running low: time to suggest a top-up.
    low: bool
    # Prep kits still free to make, without credits.
    free_kits: int


class HoldOut(BaseModel):
    """A kit's hold: whether it uses a free kit instead of credits."""

    free: bool


class OwnersIn(BaseModel):
    owner_ids: list[str] = Field(max_length=MAX_PAGE_SIZE)


class EntryOut(BaseModel):
    """One line of a wallet's history."""

    amount: int
    reason: str
    note: str | None
    created_at: datetime


class SpendIn(BaseModel):
    """A charge for something delivered at once. `key` makes a repeat count once."""

    owner_id: str
    key: str
    note: str | None = None
    # A certificate on a public kit: the kit's author, who gets a share.
    author_id: str | None = None


class WelcomeIn(BaseModel):
    owner_email: str
    # The code of the link the owner came through, and their other companies, which can't
    # refer this one.
    referral: str | None = None
    related: list[str] = Field(default=[], max_length=MAX_PAGE_SIZE)


class ReferralOut(BaseModel):
    """The owner's referral link code, what it earns, and how many it has earned for."""

    code: str
    reward: int
    min_dollars: int
    rewarded: int


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
