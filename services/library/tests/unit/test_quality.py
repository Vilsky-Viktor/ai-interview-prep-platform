import asyncio
import uuid
from types import SimpleNamespace

from app.constants.quality import QualityFlag
from app.helpers.quality import flag_for
from app.integrations import generation
from app.services import outbox
from app.services.quality import review
from app.storage import preparations, quality

QUESTION_ID = uuid.uuid4()
OPTIONS = [
    {"answer": "Debit cash", "correct": True},
    {"answer": "Credit cash", "correct": False},
    {"answer": "Debit revenue", "correct": False},
    {"answer": "Credit expenses", "correct": False},
]


def flag(answers=0, correct=0, picks=None, reports=None, likes=0, dislikes=0):
    return flag_for(OPTIONS, answers, correct, picks or {}, reports or {}, likes, dislikes)


def even_picks(right):
    """`right` picks of the correct option and 10 of each wrong one."""
    return {"Debit cash": right, "Credit cash": 10, "Debit revenue": 10, "Credit expenses": 10}


def test_a_new_question_is_not_flagged():
    assert flag() is None
    assert flag(answers=10, correct=0, picks={"Credit cash": 10}) is None


def test_a_wrong_option_beating_the_key_flags_it():
    picks = {"Debit cash": 8, "Credit cash": 20, "Debit revenue": 1, "Credit expenses": 1}

    assert flag(answers=30, correct=8, picks=picks) == QualityFlag.WRONG_KEY


def test_two_wrong_answer_reports_flag_the_key():
    assert flag(reports={"wrong_answer": 2}) == QualityFlag.WRONG_KEY
    assert flag(reports={"wrong_answer": 1}) is None


def test_unclear_off_topic_and_disliked_questions_are_rewritten():
    assert flag(reports={"unclear": 2}) == QualityFlag.REWRITE
    assert flag(reports={"off_topic": 2}) == QualityFlag.REWRITE
    assert flag(likes=1, dislikes=3) == QualityFlag.REWRITE
    assert flag(likes=2, dislikes=3) is None


def test_too_hard_is_rewritten():
    picks = {"Debit cash": 4, "Credit cash": 4, "Debit revenue": 4, "Credit expenses": 4}

    assert flag(answers=40, correct=4, picks=picks) == QualityFlag.REWRITE


def test_dead_or_too_easy_options_are_weak():
    dead = {"Debit cash": 30, "Credit cash": 10, "Debit revenue": 10, "Credit expenses": 0}

    assert flag(answers=50, correct=30, picks=dead) == QualityFlag.WEAK_OPTIONS
    assert flag(answers=60, correct=30, picks=even_picks(30)) is None


def stored(flag=None, kept=False, answers=0):
    question = SimpleNamespace(text="Which entry records a cash sale?", options=OPTIONS)
    stats = SimpleNamespace(answers=answers, correct=0, option_picks={}, flag=flag, kept=kept)

    return question, stats, {"wrong_answer": 2}, 0, 0


def record(monkeypatch, found, generation_down=False):
    calls = []

    async def fake_load(_question_id):
        return found

    async def fake_verify(question_id, flag):
        if generation_down:
            raise ConnectionError("generation is down")

        calls.append(("verify", flag))

    async def fake_save(question_id, flag, kept=False, notice=None):
        calls.append(("save", flag))

    async def fake_set(_question_id):
        return SimpleNamespace(id=uuid.uuid4(), owner_type="user", owner_id="u1", title="Kit")

    async def fake_topic(_question_id):
        return "Bookkeeping"

    async def fake_flush():
        pass

    monkeypatch.setattr(quality, "load", fake_load)
    monkeypatch.setattr(generation, "verify_question", fake_verify)
    monkeypatch.setattr(quality, "save_flag", fake_save)
    monkeypatch.setattr(preparations, "get_for_question", fake_set)
    monkeypatch.setattr(preparations, "topic_of_question", fake_topic)
    monkeypatch.setattr(outbox, "flush_quietly", fake_flush)

    return calls


def test_a_new_flag_goes_to_the_verifier_then_is_saved(monkeypatch):
    calls = record(monkeypatch, stored())

    asyncio.run(review(QUESTION_ID))

    assert calls == [("verify", QualityFlag.WRONG_KEY), ("save", QualityFlag.WRONG_KEY)]


def test_a_known_flag_is_not_sent_again(monkeypatch):
    calls = record(monkeypatch, stored(flag=QualityFlag.WRONG_KEY))

    asyncio.run(review(QUESTION_ID))

    assert calls == []


def test_a_kept_question_is_never_flagged(monkeypatch):
    calls = record(monkeypatch, stored(kept=True))

    asyncio.run(review(QUESTION_ID))

    assert calls == []


def test_flag_is_not_saved_when_the_verifier_is_unreachable(monkeypatch):
    calls = record(monkeypatch, stored(), generation_down=True)

    asyncio.run(review(QUESTION_ID))

    assert calls == []
