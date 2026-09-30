from app.constants.pricing import MODEL_PRICES


def merge_usage(total: dict, added: dict) -> dict:
    """Adds token counts per model; `added` is a usage callback's usage_metadata."""
    merged = {model: dict(counts) for model, counts in total.items()}

    for model, counts in added.items():
        current = merged.setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        current["input_tokens"] += counts.get("input_tokens", 0)
        current["output_tokens"] += counts.get("output_tokens", 0)

    return merged


def model_price(model: str) -> tuple[float, float] | None:
    """Responses name dated models, e.g. gpt-4o-mini-2024-07-18; the longest known prefix wins."""
    known = [name for name in MODEL_PRICES if model.startswith(name)]

    return MODEL_PRICES[max(known, key=len)] if known else None


def cost_usd(usage: dict | None) -> float | None:
    """Total cost of the usage, or None if it is empty or includes a model without a price."""
    if not usage:
        return None

    total = 0.0

    for model, counts in usage.items():
        price = model_price(model)

        if price is None:
            return None

        total += (counts["input_tokens"] * price[0] + counts["output_tokens"] * price[1]) / 1e6

    return round(total, 4)
