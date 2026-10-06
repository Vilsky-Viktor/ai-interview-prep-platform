import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.constants.generation import VERIFY_QUESTION
from app.constants.quality import QualityFlag
from app.integrations import library, llm
from app.schemas.questions import AnswerItem, AnswerList
from app.schemas.regenerate import QuestionContext, RegeneratedOption
from app.schemas.verify import KeyCheck, QuestionQuality, ReportNote
from app.services import verify as verify_service
from app.services.verify import check_key, verify
from app.storage import key_checks

QUESTION_ID = uuid.uuid4()
TEXT = "A customer pays cash. Which entry is recorded?"


def context():
    return QuestionContext(
        set_id=uuid.uuid4(),
        kind="preparation",
        owner_id="ann",
        level="basic",
        topic="Bookkeeping",
        subtopics=[],
        existing=[TEXT],
    )


def question():
    # The key is on "Credit cash", but people pick "Debit cash".
    return QuestionQuality(
        text=TEXT,
        options=[
            RegeneratedOption(answer="Debit cash", correct=False),
            RegeneratedOption(answer="Credit cash", correct=True),
            RegeneratedOption(answer="Debit revenue", correct=False),
            RegeneratedOption(answer="Credit expenses", correct=False),
        ],
        answers=40,
        option_picks={"Debit cash": 30, "Credit cash": 6, "Debit revenue": 2, "Credit expenses": 2},
        reports=[ReportNote(reason="wrong_answer", comment="Cash comes in, so it's a debit")],
    )


class FakeLLM:
    def __init__(self, result):
        self.result = result
        self.prompts = []

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, messages):
        self.prompts.append(messages[0].content)

        return self.result


def record(monkeypatch, verdict=None, flag=None):
    """Fakes the library and the models; the library's question carries `flag`."""
    calls = []

    async def fake_context(_question_id):
        return context()

    async def fake_quality(_question_id):
        return question().model_copy(update={"flag": flag})

    async def fake_keep(question_id):
        calls.append(("keep", question_id))

    async def fake_replace(question_id, new):
        calls.append(("replace", new.text, [option.correct for option in new.options]))

    async def fake_regenerate(question_id, _context):
        calls.append(("regenerate", question_id))

    fake_llm = FakeLLM(verdict)
    monkeypatch.setattr(library, "get_question_context", fake_context)
    monkeypatch.setattr(library, "get_question_quality", fake_quality)
    monkeypatch.setattr(library, "keep_question", fake_keep)
    monkeypatch.setattr(library, "replace_question", fake_replace)
    monkeypatch.setattr(verify_service, "regenerate", fake_regenerate)
    monkeypatch.setattr(llm, "get_verifier_llm", lambda: fake_llm)

    return calls, fake_llm


def test_a_wrong_key_is_moved_to_the_right_option(monkeypatch):
    # The marked option is listed first, so "Debit cash" is number 1.
    calls, fake_llm = record(monkeypatch, KeyCheck(correct_index=1))

    asyncio.run(check_key(QUESTION_ID, question(), context()))

    assert calls == [("replace", TEXT, [True, False, False, False])]
    assert "0. Credit cash (picked 6 times)" in fake_llm.prompts[0]
    # The reason is counted; the reporter's own words never reach the model.
    assert "wrong_answer: 1" in fake_llm.prompts[0]
    assert "Cash comes in" not in fake_llm.prompts[0]


def test_a_confirmed_key_keeps_the_question(monkeypatch):
    calls, _ = record(monkeypatch, KeyCheck(correct_index=0))

    asyncio.run(check_key(QUESTION_ID, question(), context()))

    assert calls == [("keep", QUESTION_ID)]


def test_a_question_without_one_right_option_is_replaced(monkeypatch):
    calls, _ = record(monkeypatch, KeyCheck(correct_index=None))

    asyncio.run(check_key(QUESTION_ID, question(), context()))

    assert calls == [("regenerate", QUESTION_ID)]


def test_a_wrong_key_waits_for_the_next_batch(monkeypatch):
    calls, fake_llm = record(monkeypatch, KeyCheck(correct_index=1), QualityFlag.WRONG_KEY)
    queued = []

    async def fake_add(question_id, text, marked):
        queued.append((question_id, text, marked))

    monkeypatch.setattr(key_checks, "add", fake_add)

    asyncio.run(verify(QUESTION_ID, QualityFlag.WRONG_KEY))

    # The key it's checked against is kept, so a result for a key moved since is dropped.
    assert queued == [(QUESTION_ID, TEXT, "Credit cash")]
    assert calls == []
    assert fake_llm.prompts == []


def test_a_flagged_rewrite_replaces_the_question(monkeypatch):
    calls, _ = record(monkeypatch, flag=QualityFlag.REWRITE)

    asyncio.run(verify(QUESTION_ID, QualityFlag.REWRITE))

    assert calls == [("regenerate", QUESTION_ID)]


def test_weak_options_are_written_again_for_the_same_question(monkeypatch):
    calls, _ = record(monkeypatch, flag=QualityFlag.WEAK_OPTIONS)
    answers = AnswerList(
        answers=[
            AnswerItem(
                id=0,
                correct_option="Debit cash",
                distractors=["Credit cash", "Debit capital", "Credit revenue"],
                ambiguous=False,
            )
        ]
    )
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM(answers))

    asyncio.run(verify(QUESTION_ID, QualityFlag.WEAK_OPTIONS))

    assert len(calls) == 1
    assert calls[0][:2] == ("replace", TEXT)
    assert sorted(calls[0][2]) == [False, False, False, True]


def test_a_question_kept_or_replaced_since_it_was_flagged_is_skipped(monkeypatch):
    calls, _ = record(monkeypatch, flag=None)

    asyncio.run(verify(QUESTION_ID, QualityFlag.REWRITE))

    assert calls == []


def test_the_librarys_current_flag_wins_over_the_one_sent(monkeypatch):
    calls, _ = record(monkeypatch, flag=QualityFlag.REWRITE)

    asyncio.run(verify(QUESTION_ID, QualityFlag.WRONG_KEY))

    assert calls == [("regenerate", QUESTION_ID)]


def test_a_deleted_question_is_skipped(monkeypatch):
    calls, _ = record(monkeypatch)

    async def gone(_question_id):
        return None

    monkeypatch.setattr(library, "get_question_quality", gone)

    asyncio.run(verify(QUESTION_ID, QualityFlag.REWRITE))

    assert calls == []


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
    import asyncio
    from types import SimpleNamespace

    from app.integrations import library
    from app.services import verify as verify_service
    from app.storage import key_checks

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
