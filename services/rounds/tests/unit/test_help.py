import json

from firebase_admin import auth as firebase_auth
from prepza_common.constants import MAX_OWNED_COMPANIES

from app.constants.help import (
    HELP_HISTORY_CHARACTERS,
    HELP_HISTORY_MESSAGES,
    MAX_HELP_QUESTION_LENGTH,
)
from app.constants.terms import TERMS_SECTIONS
from app.helpers.help import guide
from app.schemas.help import HelpMessage
from app.services.help import build_messages

CATALOG = {
    "environment": "sandbox",
    "client_token": "secret-token",
    "candidate_credits": 300,
    "welcome_company": 900,
}


def fake_catalog(catalog):
    async def get():
        return catalog

    return get


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

    assert f"can own up to {MAX_OWNED_COMPANIES}" in system
    assert "Refunds: you can ask for a refund" in system
    assert "Who is responsible" in system
    assert '"candidate_credits": 300' in system
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


def test_long_earlier_messages_are_left_out_but_the_question_stays():
    long = "x" * (HELP_HISTORY_CHARACTERS // 2 + 1)
    conversation = [
        HelpMessage(role="user", content="first"),
        HelpMessage(role="assistant", content=long),
        HelpMessage(role="user", content="again"),
        HelpMessage(role="assistant", content=long),
        HelpMessage(role="user", content="last question"),
    ]
    messages = build_messages(conversation, "en", None)

    # The latest long answer and the question before it fit; the earlier long one doesn't.
    assert [message.content for message in messages[1:]] == ["again", long, "last question"]


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


def test_accounts_addresses_and_the_daily_total_are_limited(client, monkeypatch):
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
    # Behind Google's load balancer: the visitor's own header, then their address and the
    # balancer's.
    forwarded = {"X-Forwarded-For": "1.1.1.1, 203.0.113.7, 35.191.0.1"}
    client.post("/help/chat", json=body, headers={"Authorization": "Bearer token", **forwarded})

    assert keys == [
        "rate:help:ip:testclient",
        "rate:help:all",
        "rate:help:u1",
        "rate:help:ip:203.0.113.7",
        "rate:help:all",
    ]


def test_visitors_send_contact_messages(client, monkeypatch):
    saved = []

    async def fake_save(data):
        saved.append(data)

    async def fake_flush():
        return None

    monkeypatch.setattr("app.routers.help.contact_store.save", fake_save)
    monkeypatch.setattr("app.routers.help.outbox_service.flush_quietly", fake_flush)
    body = {"name": " Ann ", "email": "ann@example.com", "message": "Do you offer invoices?"}

    response = client.post("/help/contact", json=body, headers={"Accept-Language": "de"})

    assert response.status_code == 204
    assert saved == [
        {
            "name": "Ann",
            "email": "ann@example.com",
            "message": "Do you offer invoices?",
            "language": "de",
        }
    ]


def test_contact_messages_are_limited_per_address_and_in_all(client, monkeypatch):
    keys = []

    async def record(redis, key, limit, window):
        keys.append(key)

    async def fake_save(data):
        return None

    async def fake_flush():
        return None

    monkeypatch.setattr("app.routers.help.hit", record)
    monkeypatch.setattr("app.routers.help.contact_store.save", fake_save)
    monkeypatch.setattr("app.routers.help.outbox_service.flush_quietly", fake_flush)
    body = {"name": "Ann", "email": "ann@example.com", "message": "Hi"}

    client.post("/help/contact", json=body)

    assert keys == ["rate:contact:ip:testclient", "rate:contact:all"]


def test_contact_messages_need_every_field(client):
    body = {"name": "Ann", "email": "ann@example.com", "message": "Hi"}

    assert client.post("/help/contact", json={**body, "email": "not-an-email"}).status_code == 422
    assert client.post("/help/contact", json={**body, "name": "  "}).status_code == 422
    assert client.post("/help/contact", json={**body, "message": ""}).status_code == 422


def test_billings_prices_are_kept_for_a_while(monkeypatch):
    import asyncio

    import httpx
    from prepza_common import memory_cache

    from app.integrations import billing

    calls = []

    class FakeClient:
        async def get(self, url):
            calls.append(url)

            return httpx.Response(200, json=CATALOG, request=httpx.Request("GET", url))

    monkeypatch.setattr(memory_cache, "_entries", {})
    monkeypatch.setattr("app.integrations.billing.http.get_client", lambda: FakeClient())

    assert asyncio.run(billing.catalog()) == CATALOG
    assert asyncio.run(billing.catalog()) == CATALOG
    assert len(calls) == 1


def test_the_chat_and_the_platform_guide_share_one_text():
    from app.helpers.help import knowledge

    question = [HelpMessage(role="user", content="How do refunds work?")]
    system = build_messages(question, "de", CATALOG)[0].content

    assert knowledge("en", CATALOG) in system


def test_the_platform_guide_is_served_in_the_pages_language(client, monkeypatch):
    from prepza_common import memory_cache

    from app.constants.faq import FAQS

    calls = []

    async def catalog():
        calls.append(1)

        return CATALOG

    monkeypatch.setattr(memory_cache, "_entries", {})
    monkeypatch.setattr("app.services.help.billing.catalog", catalog)

    german = client.get("/help/guide", headers={"Accept-Language": "de"})
    english = client.get("/help/guide")
    client.get("/help/guide", headers={"Accept-Language": "de"})

    assert german.status_code == 200
    assert german.headers["content-type"].startswith("text/plain")
    assert f"Q: {FAQS['de'][0]['question']}" in german.text
    assert f"Q: {FAQS['en'][0]['question']}" in english.text
    assert f"can own up to {MAX_OWNED_COMPANIES}" in german.text
    assert "secret-token" not in german.text
    # Kept per language: the second German request is built from memory.
    assert len(calls) == 2
