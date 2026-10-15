import asyncio

from fastapi import HTTPException
from prepza_common import rate_limit

from app.constants.help import HELP_MAX_OUTPUT_TOKENS, HELP_SPEND_KEY
from app.integrations import llm
from app.services import help as help_service
from tests.unit.test_help import CATALOG, fake_catalog

BODY = {"messages": [{"role": "user", "content": "How do I start?"}]}


def test_an_answer_that_fails_halfway_still_counts_its_tokens_estimated(
    client, monkeypatch, help_spending
):
    async def failing(messages, used):
        yield "x" * 40
        raise TimeoutError

    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))
    monkeypatch.setattr("app.routers.help.stream_reply", failing)

    client.post("/help/chat", json=BODY)

    # The model read the guide and the question, and wrote 40 characters: about 10 tokens.
    [(_, checked), (_, spent)] = help_spending
    assert checked == 0
    assert spent > 10


def test_an_answer_counts_its_tokens_against_the_days_budget(client, monkeypatch, help_spending):
    async def fake_stream(messages, used):
        used["tokens"] = 1_234
        yield "Paste a job description."

    monkeypatch.setattr("app.routers.help.billing.catalog", fake_catalog(CATALOG))
    monkeypatch.setattr("app.routers.help.stream_reply", fake_stream)

    response = client.post("/help/chat", json=BODY)

    assert response.status_code == 200
    # Checked before the answer (0), then counted after it.
    assert help_spending == [(HELP_SPEND_KEY, 0), (HELP_SPEND_KEY, 1_234)]


def test_a_spent_budget_refuses_new_questions(client, monkeypatch):
    async def spent(redis, key, amount, limit, window, message=None):
        raise HTTPException(429, "Too many requests. Try again later.")

    async def never(messages, used):
        raise AssertionError("asked the model")
        yield ""

    monkeypatch.setattr("app.routers.help.spend", spent)
    monkeypatch.setattr("app.routers.help.stream_reply", never)

    assert client.post("/help/chat", json=BODY).status_code == 429


def test_going_over_with_an_answer_still_keeps_it(monkeypatch):
    async def over(redis, key, amount, limit, window, message=None):
        raise HTTPException(429, "Too many requests. Try again later.")

    monkeypatch.setattr(rate_limit, "spend", over)

    # No exception: the next question is the one refused.
    asyncio.run(help_service.record_spend(None, 5_000))


def test_an_answer_is_capped_and_reports_its_tokens(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    llm.get_help_llm.cache_clear()
    model = llm.get_help_llm()

    assert model.max_tokens == HELP_MAX_OUTPUT_TOKENS
    assert model.stream_usage is True
    llm.get_help_llm.cache_clear()
