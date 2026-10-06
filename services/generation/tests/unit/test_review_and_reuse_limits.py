import asyncio
import uuid

import pytest
from fastapi import HTTPException
from prepza_common.sets import QuestionIn

from app.constants.generation import MAX_TOPIC_REVISIONS
from app.integrations import library, llm
from app.models.generation import Generation
from app.schemas.generation import ReviewRequest
from app.services import review, schedules
from app.services.nodes.reuse import find_reused
from app.storage import generations
from tests.unit.test_language import Recorder


def awaiting_review():
    return Generation(
        id=uuid.uuid4(),
        status="awaiting_review",
        topics=[{"main_topic": "Python", "subtopics": []}, {"main_topic": "SQL", "subtopics": []}],
    )


class CountingRedis:
    """prepza_common.rate_limit.hit's SET NX + INCR, counted per key."""

    def __init__(self):
        self.counts = {}

    def pipeline(self, transaction):
        return CountingPipeline(self.counts)


class CountingPipeline:
    def __init__(self, counts):
        self.counts = counts

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def set(self, key, value, ex, nx):
        self.key = key

    def incr(self, key):
        pass

    async def execute(self):
        self.counts[self.key] = self.counts.get(self.key, 0) + 1

        return [True, self.counts[self.key]]


@pytest.fixture
def claimed(monkeypatch):
    """Reviews that got past the checks to the claim."""
    claims = []

    async def claim_review(generation_id):
        claims.append(generation_id)

        return True

    async def get(generation_id):
        return awaiting_review()

    monkeypatch.setattr(generations, "claim_review", claim_review)
    monkeypatch.setattr(generations, "get", get)

    return claims


def test_a_selection_outside_the_drafted_topics_is_refused(claimed):
    with pytest.raises(HTTPException) as refused:
        asyncio.run(review.submit_review(awaiting_review(), ReviewRequest(selected=[0, 2])))

    assert refused.value.status_code == 422
    assert claimed == []


def test_topics_are_revised_in_words_a_limited_number_of_times(claimed, monkeypatch):
    redis = CountingRedis()
    monkeypatch.setattr(review, "get_redis", lambda: redis)
    generation = awaiting_review()
    body = ReviewRequest(selected=[0], instructions="Merge them")

    for _ in range(MAX_TOPIC_REVISIONS):
        asyncio.run(review.submit_review(generation, body))

    with pytest.raises(HTTPException) as limited:
        asyncio.run(review.submit_review(generation, body))

    assert limited.value.status_code == 429
    # Approving without instructions isn't limited.
    asyncio.run(review.submit_review(generation, ReviewRequest(selected=[0])))
    assert len(claimed) == MAX_TOPIC_REVISIONS + 1


def test_a_bank_question_goes_into_one_topic_of_a_test_only(monkeypatch):
    shared = QuestionIn(text="Same?", options=[], source_id=uuid.uuid4())
    other = QuestionIn(text="Other?", options=[], source_id=uuid.uuid4())

    async def find_reusable(request):
        return [shared, other]

    monkeypatch.setattr(llm, "get_embeddings", lambda: Recorder())
    monkeypatch.setattr(library, "find_reusable", find_reusable)
    topics = [
        {"main_topic": "Python", "subtopics": []},
        {"main_topic": "Python 3", "subtopics": []},
    ]

    result = asyncio.run(find_reused({"topics": topics, "level": "mid", "language": "en"}))

    assert [[q["text"] for q in topic] for topic in result["reused"]] == [
        ["Same?", "Other?"],
        [],
    ]


def test_a_key_check_run_is_skipped_while_the_last_one_is_still_going(monkeypatch):
    runs = []

    class LockedRedis:
        async def set(self, key, value, nx, ex):
            return None

    async def collect_finished():
        runs.append("collect")

    monkeypatch.setattr(schedules, "get_redis", lambda: LockedRedis())
    monkeypatch.setattr(schedules, "collect_finished", collect_finished)

    asyncio.run(schedules.key_check_batches())

    assert runs == []


def test_key_checks_wait_during_the_emergency_pause(monkeypatch):
    runs = []

    async def on(redis):
        return True

    async def collect_finished():
        runs.append("collect")

    monkeypatch.setattr("prepza_common.pause.is_paused", on)
    monkeypatch.setattr(schedules, "get_redis", lambda: object())
    monkeypatch.setattr(schedules, "collect_finished", collect_finished)

    asyncio.run(schedules.key_check_batches())

    assert runs == []


def test_a_key_check_run_frees_only_its_own_lock(monkeypatch):
    class Redis:
        def __init__(self):
            self.values = {}

        async def set(self, key, value, nx, ex):
            assert ex >= 30 * 60

            if key in self.values:
                return None

            self.values[key] = value

            return True

        async def eval(self, script, count, key, token):
            # What the script does: delete only when the token still matches.
            if self.values.get(key) == token:
                del self.values[key]

    redis = Redis()

    async def outlived():
        # The lock ran out mid-run and the next run took it.
        redis.values["lock:key-check-batches"] = "next run"

    async def nothing():
        return None

    monkeypatch.setattr(schedules, "get_redis", lambda: redis)
    monkeypatch.setattr(schedules, "collect_finished", outlived)
    monkeypatch.setattr(schedules, "submit_pending", nothing)

    asyncio.run(schedules.key_check_batches())

    assert redis.values == {"lock:key-check-batches": "next run"}
