import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt

from app.constants.generation import VERIFY_QUESTION
from app.constants.quality import QualityFlag
from app.integrations import library
from app.services import verify as verify_service
from app.storage import key_checks

QUESTION_ID = uuid.uuid4()


def no_verify_budget_used(monkeypatch):
    from app.services import budget

    async def count_today(key):
        return 1

    monkeypatch.setattr(budget, "count_today", count_today)


def test_verify_endpoint_queues_the_worker_job(client, queued, monkeypatch):
    no_verify_budget_used(monkeypatch)
    exp = datetime.now(UTC) + timedelta(seconds=60)
    service_token = jwt.encode(
        {"iss": "library", "aud": "generation", "exp": exp},
        "test-secret-that-is-at-least-32-bytes",
        algorithm="HS256",
    )

    response = client.post(
        f"/internal/questions/{QUESTION_ID}/verify",
        json={"flag": "wrong_key"},
        headers={"Authorization": f"Bearer {service_token}"},
    )

    assert response.status_code == 202
    assert queued == [
        (
            VERIFY_QUESTION,
            {"question_id": str(QUESTION_ID), "flag": QualityFlag.WRONG_KEY, "now": False},
        )
    ]


def test_fix_now_checks_a_wrong_key_at_once_instead_of_batching(monkeypatch):

    calls = []

    async def context(_question_id):
        options = [SimpleNamespace(answer="A", correct=True)]

        return SimpleNamespace(text="Q?", flag=QualityFlag.WRONG_KEY, options=options)

    async def check_key(question_id, question, found_context):
        calls.append("now")

    async def add(question_id, text, marked):
        calls.append("batch")

    async def remove(question_ids):
        calls.append("dropped from the batch")

    monkeypatch.setattr(library, "get_question_context", context)
    monkeypatch.setattr(library, "get_question_quality", lambda _id: context(_id))
    monkeypatch.setattr(verify_service, "check_key", check_key)
    monkeypatch.setattr(key_checks, "add", add)
    monkeypatch.setattr(key_checks, "remove", remove)

    asyncio.run(verify_service.verify(QUESTION_ID, QualityFlag.WRONG_KEY, now=True))
    asyncio.run(verify_service.verify(QUESTION_ID, QualityFlag.WRONG_KEY))

    # A check of the same question still waiting in a batch is dropped first.
    assert calls == ["dropped from the batch", "now", "batch"]


def test_verify_jobs_past_the_daily_cap_are_refused_but_fix_now_is_not(client, queued, monkeypatch):
    from app.constants.quality import DAILY_VERIFY_LIMIT
    from app.services import budget

    async def count_today(key):
        return DAILY_VERIFY_LIMIT + 1

    monkeypatch.setattr(budget, "count_today", count_today)
    exp = datetime.now(UTC) + timedelta(seconds=60)
    service_token = jwt.encode(
        {"iss": "library", "aud": "generation", "exp": exp},
        "test-secret-that-is-at-least-32-bytes",
        algorithm="HS256",
    )
    url = f"/internal/questions/{QUESTION_ID}/verify"
    headers = {"Authorization": f"Bearer {service_token}"}

    assert client.post(url, json={"flag": "rewrite"}, headers=headers).status_code == 503
    assert queued == []
    assert (
        client.post(url, json={"flag": "rewrite", "now": True}, headers=headers).status_code == 202
    )
    assert len(queued) == 1
