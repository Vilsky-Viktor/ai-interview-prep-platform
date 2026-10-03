import json

from prepza_common.constants import (
    DEFAULT_QUESTION_SECONDS,
    INTERVIEWS_PER_DAY,
    LANGUAGES,
    MAX_OWNED_COMPANIES,
    MAX_SHARES,
)

from app.constants.rounds import PUBLIC_TOPICS_PER_DAY
from app.prompts.help import PLATFORM_GUIDE

# Catalog fields only Paddle.js needs; they say nothing about prices.
CATALOG_INTERNALS = {"environment", "client_token"}


def guide() -> str:
    return PLATFORM_GUIDE.format(
        max_shares=MAX_SHARES,
        public_topics=PUBLIC_TOPICS_PER_DAY,
        max_companies=MAX_OWNED_COMPANIES,
        interviews_per_day=INTERVIEWS_PER_DAY,
        question_seconds=DEFAULT_QUESTION_SECONDS,
        language_count=len(LANGUAGES),
        languages=", ".join(LANGUAGES.values()),
    )


def faq_values(catalog: dict | None) -> dict:
    """What the FAQ's answers name: prices from billing, and the number of languages."""
    prices = catalog or {}

    return {
        "count": len(LANGUAGES),
        "kit": prices.get("kit_credits", ""),
        "welcome": prices.get("welcome_user", ""),
        "candidate": prices.get("candidate_credits", ""),
        "company": prices.get("welcome_company", ""),
    }


def faq_items(faq: list[dict], catalog: dict | None) -> list[dict]:
    values = faq_values(catalog)

    return [
        {
            "key": item["key"],
            "question": item["question"],
            "answer": item["answer"].format(**values),
        }
        for item in faq
    ]


def faq_text(faq: list[dict], catalog: dict | None) -> str:
    return "\n\n".join(
        f"Q: {item['question']}\nA: {item['answer']}" for item in faq_items(faq, catalog)
    )


def prices_text(catalog: dict | None) -> str:
    """Billing's catalog as it is: its field names say what each number is."""
    if catalog is None:
        return "Not available right now; the pricing page lists every price."

    public = {key: value for key, value in catalog.items() if key not in CATALOG_INTERNALS}

    return json.dumps(public, indent=1)


def legal_text(intro: str, sections: list[dict]) -> str:
    parts = [intro]

    for section in sections:
        parts.append(section["heading"])
        parts.extend(section.get("paragraphs", []))
        parts.extend(f"- {item}" for item in section.get("items", []))

    return "\n".join(parts)
