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


def record(monkeypatch, verdict=None):
    calls = []

    async def fake_context(_question_id):
        return context()

    async def fake_quality(_question_id):
        return question()

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
    assert "wrong_answer: Cash comes in" in fake_llm.prompts[0]


def test_a_confirmed_key_keeps_the_question(monkeypatch):
    calls, _ = record(monkeypatch, KeyCheck(correct_index=0))

    asyncio.run(check_key(QUESTION_ID, question(), context()))

    assert calls == [("keep", QUESTION_ID)]


def test_a_question_without_one_right_option_is_replaced(monkeypatch):
    calls, _ = record(monkeypatch, KeyCheck(correct_index=None))

    asyncio.run(check_key(QUESTION_ID, question(), context()))

    assert calls == [("regenerate", QUESTION_ID)]


def test_a_wrong_key_waits_for_the_next_batch(monkeypatch):
    calls, fake_llm = record(monkeypatch, KeyCheck(correct_index=1))
    queued = []

    async def fake_add(question_id, text):
        queued.append((question_id, text))

    monkeypatch.setattr(key_checks, "add", fake_add)

    asyncio.run(verify(QUESTION_ID, QualityFlag.WRONG_KEY))

    assert queued == [(QUESTION_ID, TEXT)]
    assert calls == []
    assert fake_llm.prompts == []


def test_a_flagged_rewrite_replaces_the_question(monkeypatch):
    calls, _ = record(monkeypatch)

    asyncio.run(verify(QUESTION_ID, QualityFlag.REWRITE))

    assert calls == [("regenerate", QUESTION_ID)]


def test_weak_options_are_written_again_for_the_same_question(monkeypatch):
    calls, _ = record(monkeypatch)
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
    monkeypatch.setattr(llm, "get_llm", lambda: FakeLLM(answers))

    asyncio.run(verify(QUESTION_ID, QualityFlag.WEAK_OPTIONS))

    assert len(calls) == 1
    assert calls[0][:2] == ("replace", TEXT)
    assert sorted(calls[0][2]) == [False, False, False, True]


def test_a_deleted_question_is_skipped(monkeypatch):
    calls, _ = record(monkeypatch)

    async def gone(_question_id):
        return None

    monkeypatch.setattr(library, "get_question_quality", gone)

    asyncio.run(verify(QUESTION_ID, QualityFlag.REWRITE))

    assert calls == []


def test_verify_endpoint_queues_the_worker_job(client, queued):
    exp = datetime.now(UTC) + timedelta(seconds=60)
    service_token = jwt.encode(
        {"iss": "library", "exp": exp}, "test-secret-that-is-at-least-32-bytes", algorithm="HS256"
    )

    response = client.post(
        f"/internal/questions/{QUESTION_ID}/verify",
        json={"flag": "wrong_key"},
        headers={"Authorization": f"Bearer {service_token}"},
    )

    assert response.status_code == 202
    assert queued == [
        (VERIFY_QUESTION, {"question_id": str(QUESTION_ID), "flag": QualityFlag.WRONG_KEY})
    ]
