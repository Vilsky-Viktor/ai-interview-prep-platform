from app.config.settings import settings
from app.helpers.payload import build_preparation
from app.helpers.progress import track_progress
from app.helpers.questions import clean_distractors, merge_buckets
from app.helpers.usage import cost_usd, merge_usage


def test_merge_buckets_round_robin_and_dedupe():
    buckets = [["A1", "A2", "A3"], ["a1", "B1"], []]

    assert merge_buckets(buckets, 3) == ["A1", "B1", "A2"]


def test_clean_distractors_drops_correct_and_duplicates():
    assert clean_distractors([" Wrong ", "wrong", "Right", ""], "right") == ["Wrong"]


def test_track_progress(monkeypatch):
    monkeypatch.setattr(settings, "questions_per_topic", 100)
    progress = {}
    topics = [{"main_topic": "T", "subtopics": ["a", "b"]}]

    assert not track_progress(progress, {"generate_topics": {"topics": topics}})
    assert track_progress(progress, {"human_review": {"topics": topics, "approved": True}})
    assert progress == {"done": 0, "total": 12, "question_steps": 2}

    track_progress(progress, {"generate_questions": {}})
    track_progress(progress, {"merge_questions": {"topic_questions": [["q"] * 25]}})

    assert progress["done"] == 1
    assert progress["total"] == 5


def test_build_preparation_skips_incomplete_questions():
    options = [{"answer": "x", "correct": True}]
    values = {
        "title": "Title",
        "level": "medium",
        "requirements": ["Python"],
        "final": [
            {
                "topic": "T",
                "subtopics": ["a"],
                "questions": ["q1", "q2"],
                "answers": ["a1", ""],
                "answer_options": [options, []],
            }
        ],
    }

    preparation = build_preparation("uid", "text", values)

    assert preparation.title == "Title"
    assert [q.text for q in preparation.topics[0].questions] == ["q1"]


def test_merge_usage_adds_tokens_per_model():
    total = {"gpt-4o-2024-08-06": {"input_tokens": 100, "output_tokens": 10}}
    added = {
        "gpt-4o-2024-08-06": {"input_tokens": 50, "output_tokens": 5, "total_tokens": 55},
        "gpt-4o-mini-2024-07-18": {"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
    }

    assert merge_usage(total, added) == {
        "gpt-4o-2024-08-06": {"input_tokens": 150, "output_tokens": 15},
        "gpt-4o-mini-2024-07-18": {"input_tokens": 7, "output_tokens": 3},
    }
    assert total["gpt-4o-2024-08-06"]["input_tokens"] == 100


def test_cost_uses_the_longest_matching_model_price():
    usage = {
        "gpt-4o-2024-08-06": {"input_tokens": 1_000_000, "output_tokens": 100_000},
        "gpt-4o-mini-2024-07-18": {"input_tokens": 1_000_000, "output_tokens": 0},
    }

    # gpt-4o: 2.50 + 0.10 * 10.00; gpt-4o-mini: 0.15.
    assert cost_usd(usage) == 3.65


def test_cost_is_unknown_for_an_unpriced_model_or_no_usage():
    assert cost_usd({"some-model": {"input_tokens": 1, "output_tokens": 1}}) is None
    assert cost_usd(None) is None
    assert cost_usd({}) is None
