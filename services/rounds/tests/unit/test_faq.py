import string

from prepza_common.constants import LANGUAGES

from app.constants.faq import FAQS, with_english
from app.constants.faq.de import FAQ as GERMAN
from tests.unit.test_help import CATALOG, fake_catalog


def test_every_faq_asks_the_english_questions_with_the_same_placeholders():
    def shape(faq):
        return [
            (
                item["key"],
                {name for _, name, _, _ in string.Formatter().parse(item["answer"]) if name},
            )
            for item in faq
        ]

    assert set(FAQS) == set(LANGUAGES)
    assert all(shape(faq) == shape(FAQS["en"]) for faq in FAQS.values())


def test_a_question_not_translated_yet_shows_in_english(client, monkeypatch):
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))
    # German as it would be with its "cost" answer not translated yet.
    partly = [item for item in GERMAN if item["key"] != "cost"]
    monkeypatch.setitem(FAQS, "de", with_english(partly, FAQS["en"]))

    items = {
        item["key"]: item
        for item in client.get("/help/faq", headers={"Accept-Language": "de"}).json()
    }
    english = {item["key"]: item for item in FAQS["en"]}
    translated = {item["key"]: item for item in partly}

    assert items["expire"]["question"] == translated["expire"]["question"]
    assert items["cost"]["question"] == english["cost"]["question"]
    assert "300" in items["cost"]["answer"] and "{" not in items["cost"]["answer"]


def test_faq_names_prices_in_dollars_from_billing(client, monkeypatch):
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))

    items = {item["key"]: item["answer"] for item in client.get("/help/faq").json()}

    # 300 credits a candidate is $3, and 5 candidates a month are $180 a year.
    assert "300 credits ($3)" in items["compare_hiring"]
    assert "$180 a year" in items["compare_hiring"]
    # 900 welcome credits cover 3 candidates.
    assert "900 free credits, enough for its first 3 candidates" in items["cost"]


def test_faq_names_no_competitor_prices():
    # Other tools' prices change and aren't ours to quote: the comparison explains the pricing
    # models instead, in every language.
    for language, items in FAQS.items():
        answer = next(item["answer"] for item in items if item["key"] == "compare_hiring")

        assert "215" not in answer and "100" not in answer, language


def test_faq_says_automatic_top_up_saves_the_card_as_a_free_subscription():
    # Automatic top-up is a $0 Paddle subscription, so no language may say there are none.
    for language, items in FAQS.items():
        answer = next(item["answer"] for item in items if item["key"] == "expire")

        assert "Paddle" in answer, language


def test_faq_says_in_every_language_how_to_stop_emails():
    # Every language answers it in its own words, not in English.
    english = next(item for item in FAQS["en"] if item["key"] == "emails")

    assert "Settings" in english["answer"] and "Unsubscribe" in english["answer"]

    for language, items in FAQS.items():
        answer = next(item["answer"] for item in items if item["key"] == "emails")

        assert language == "en" or answer != english["answer"], language


def test_faq_still_shows_when_billing_is_down(client, monkeypatch):
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(None))

    response = client.get("/help/faq")

    assert response.status_code == 200
    assert len(response.json()) == len(FAQS["en"])
