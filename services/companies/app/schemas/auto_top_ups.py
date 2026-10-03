from pydantic import BaseModel


class AutoTopUpIn(BaseModel):
    """Which top-up to buy, and under which available balance (credits)."""

    product: str
    threshold: int


class CheckoutOut(BaseModel):
    """The Paddle checkout to open: its price and the custom data to send with it."""

    price_id: str
    custom_data: dict[str, str]


class AutoTopUpOut(BaseModel):
    """The company's automatic top-up, as billing has it."""

    offered: bool
    on: bool
    waiting: bool
    product: str | None
    threshold: int | None
    products: list[str]
    thresholds: list[int]
    checkout: CheckoutOut | None = None
