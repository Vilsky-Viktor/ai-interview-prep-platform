from datetime import datetime

from pydantic import BaseModel


class ProductOut(BaseModel):
    key: str
    title: str
    owner: str
    price_cents: int
    # What one purchase grants, for the pricing page.
    candidate_credits: int
    generation_credits: int
    pass_days: int
    # Paddle's price; None while the product isn't on sale yet.
    price_id: str | None


class CatalogOut(BaseModel):
    """What the pricing page and Paddle.js need; the client token is public by design."""

    environment: str
    client_token: str
    currency: str
    # What everyone gets for free.
    free_generations_per_month: int
    free_candidates: int
    products: list[ProductOut]


class PlanOut(BaseModel):
    """A learner's preparations: an active pass covers all of them."""

    pass_until: datetime | None
    generation_credits: int
    free_generations_left: int


class CompanyCreditsOut(BaseModel):
    candidate_credits: int
