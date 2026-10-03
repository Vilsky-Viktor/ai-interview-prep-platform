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
    products: list[TopUpOut]
    custom: CustomTopUpOut


class BalanceOut(BaseModel):
    balance: int
    reserved: int
    available: int


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
