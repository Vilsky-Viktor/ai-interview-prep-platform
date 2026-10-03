import json
import string

from firebase_admin import auth as firebase_auth
from prepza_common.constants import LANGUAGES, MAX_SHARES

from app.constants.faq import FAQS
from app.constants.help import HELP_HISTORY_MESSAGES, MAX_HELP_QUESTION_LENGTH
from app.constants.terms import TERMS_SECTIONS
from app.helpers.help import guide
from app.schemas.help import HelpMessage
from app.services.help import build_messages

CATALOG = {
    "environment": "sandbox",
    "client_token": "secret-token",
    "kit_credits": 500,
    "welcome_user": 500,
    "candidate_credits": 300,
    "welcome_company": 1500,
}


def fake_catalog(catalog):
    async def get():
        return catalog

    return get


def test_every_faq_has_the_same_questions_and_placeholders():
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


def test_faq_comes_in_the_page_language_with_todays_prices(client, monkeypatch):
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))

    items = client.get("/help/faq", headers={"Accept-Language": "de"}).json()
    cost = next(item for item in items if item["key"] == "cost")

    assert cost["question"] == next(i["question"] for i in FAQS["de"] if i["key"] == "cost")
    assert "500" in cost["answer"] and "{" not in cost["answer"]


def test_faq_still_shows_when_billing_is_down(client, monkeypatch):
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(None))

    response = client.get("/help/faq")

    assert response.status_code == 200
    assert len(response.json()) == len(FAQS["en"])


def test_legal_documents_are_served(client):
    terms = client.get("/help/legal/terms").json()

    assert [section["heading"] for section in terms["sections"]] == [
        section["heading"] for section in TERMS_SECTIONS
    ]
    assert client.get("/help/legal/privacy").status_code == 200
    assert client.get("/help/legal/cookies").status_code == 422


def test_the_chat_knows_the_platform_prices_and_documents():
    question = [HelpMessage(role="user", content="How do refunds work?")]
    system = build_messages(question, "de", CATALOG)[0].content

    assert f"up to {MAX_SHARES} people" in system
    assert "Refunds: you can ask for a refund" in system
    assert "Who is responsible" in system
    assert '"kit_credits": 500' in system
    assert "secret-token" not in system
    assert system.endswith(
        "Reply in German, the language of the page, unless the user writes in another language."
    )
    assert "{" not in guide()


def test_a_long_conversation_sends_only_its_latest_messages():
    conversation = [
        HelpMessage(role="user" if index % 2 == 0 else "assistant", content=f"message {index}")
        for index in range(30)
    ] + [HelpMessage(role="user", content="last question")]
    messages = build_messages(conversation, "en", None)

    assert len(messages) == 1 + HELP_HISTORY_MESSAGES + 1
    assert messages[-1].content == "last question"
    assert "pricing page lists every price" in messages[0].content


def test_visitors_can_chat_and_get_a_stream(client, monkeypatch):
    async def fake_stream(messages):
        yield "Paste "
        yield "a job description."

    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))
    monkeypatch.setattr("app.routers.help.stream_reply", fake_stream)

    response = client.post(
        "/help/chat", json={"messages": [{"role": "user", "content": "How do I start?"}]}
    )
    events = [json.loads(line[6:]) for line in response.text.split("\n\n") if line]

    assert response.status_code == 200
    assert events == [{"delta": "Paste "}, {"delta": "a job description."}, {"done": True}]


def test_the_chat_needs_a_question_last_and_not_too_long(client):
    answer_last = {"messages": [{"role": "assistant", "content": "Hi"}]}
    too_long = {"messages": [{"role": "user", "content": "x" * (MAX_HELP_QUESTION_LENGTH + 1)}]}

    assert client.post("/help/chat", json=answer_last).status_code == 422

    response = client.post("/help/chat", json=too_long, headers={"Accept-Language": "de"})

    assert response.status_code == 422
    assert "Die Frage ist zu lang." in response.text


def test_accounts_and_the_daily_total_are_limited(client, monkeypatch):
    keys = []

    async def record(redis, key, limit, window):
        keys.append(key)

    async def fake_stream(messages):
        yield "ok"

    monkeypatch.setattr("app.routers.help.hit", record)
    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(None))
    monkeypatch.setattr("app.routers.help.stream_reply", fake_stream)
    monkeypatch.setattr(firebase_auth, "verify_id_token", lambda token: {"uid": "u1"})
    body = {"messages": [{"role": "user", "content": "Hi"}]}

    client.post("/help/chat", json=body)
    client.post("/help/chat", json=body, headers={"Authorization": "Bearer token"})

    assert keys == ["rate:help:all", "rate:help:u1", "rate:help:all"]
