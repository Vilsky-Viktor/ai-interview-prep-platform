import uuid

from app.config.settings import settings
from app.helpers.payload import build_preparation
from app.helpers.progress import track_progress
from app.helpers.questions import (
    build_options,
    clean_distractors,
    merge_buckets,
    split_count,
    strip_choices,
)


def test_merge_buckets_round_robin_and_dedupe():
    def bucket(*texts):
        return [{"text": text, "options": []} for text in texts]

    merged = merge_buckets([bucket("A1", "A2", "A3"), bucket("a1", "B1"), []])

    assert [question["text"] for question in merged] == ["A1", "A2", "B1", "A3"]


def test_choices_listed_in_the_question_are_stripped():
    listed = "What does `bool([])` return?\nA. True\nB. False\nC) None\nD. An error"

    assert strip_choices(listed) == "What does `bool([])` return?"
    assert strip_choices("Which is a vowel: A or B?") == "Which is a vowel: A or B?"


def test_options_need_a_short_correct_answer_and_three_distractors():
    options = build_options(" Right ", ["W1", "W2", "W3", "W4"])

    assert sorted(option["answer"] for option in options) == ["Right", "W1", "W2", "W3"]
    assert build_options("Right", ["W1", "W2"]) is None
    assert build_options("x" * 251, ["W1", "W2", "W3"]) is None


def test_counts_are_split_evenly():
    assert split_count(55, 3) == [19, 18, 18]
    assert split_count(2, 3) == [1, 1, 0]


def test_clean_distractors_drops_correct_and_duplicates():
    assert clean_distractors([" Wrong ", "wrong", "Right", ""], "right", 250) == ["Wrong"]


def test_clean_distractors_drops_options_over_the_length_limit():
    assert clean_distractors(["Short", "x" * 11], "Right", 10) == ["Short"]


def test_track_progress(monkeypatch):
    monkeypatch.setattr(settings, "questions_per_topic", 100)
    progress = {}
    # 110 questions over two subtopics: 55 each, written in 3 calls of up to 20.
    topics = [{"main_topic": "T", "subtopics": ["a", "b"]}]

    assert not track_progress(progress, {"generate_topics": {"topics": topics}})
    assert track_progress(progress, {"human_review": {"topics": topics, "approved": True}})
    assert progress["done"] == 0
    assert progress["total"] == 6
    assert progress["topics"] == 1
    assert progress["topics_ready"] == 0

    call = {"generate_questions": {"question_pool": [{"topic_index": 0}]}}
    track_progress(progress, call)

    assert progress["done"] == 1

    for _ in range(5):
        track_progress(progress, call)

    assert progress["topics_ready"] == 1

    track_progress(progress, {"merge_questions": {"topic_questions": [[]]}})

    assert progress["done"] == progress["total"] == 6


def test_progress_never_passes_100_percent_when_a_retry_replays_steps(monkeypatch):
    monkeypatch.setattr(settings, "questions_per_topic", 10)
    topics = [{"main_topic": "T", "subtopics": ["a", "b"]}]
    progress = {}
    track_progress(progress, {"human_review": {"topics": topics, "approved": True}})

    # A retry replays question steps that had already finished.
    for _ in range(5):
        track_progress(progress, {"generate_questions": {"question_pool": [{"topic_index": 0}]}})

    assert (progress["done"], progress["total"], progress["topic_done"]) == (1, 2, [2])

    track_progress(progress, {"merge_questions": {"topic_questions": [[]]}})

    assert (progress["done"], progress["total"], progress["topics_ready"]) == (2, 2, 1)


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
                "answer_options": [options, []],
            }
        ],
    }

    generation_id = uuid.uuid4()
    preparation = build_preparation(generation_id, "uid", "text", values)

    assert preparation.title == "Title"
    assert [q.text for q in preparation.topics[0].questions] == ["q1"]
    assert preparation.model_dump(mode="json")["generation_id"] == str(generation_id)


def test_spare_questions_replace_dropped_ones_up_to_the_count(monkeypatch):
    monkeypatch.setattr(settings, "questions_per_topic", 2)
    options = [{"answer": "x", "correct": True}]
    values = {
        "title": "Title",
        "level": "medium",
        "requirements": ["Python"],
        "final": [
            {
                "topic": "T",
                "subtopics": ["a"],
                "questions": ["q1", "ambiguous", "q2", "spare"],
                "answer_options": [options, [], options, options],
            }
        ],
    }

    preparation = build_preparation(uuid.uuid4(), "uid", "text", values)

    assert [q.text for q in preparation.topics[0].questions] == ["q1", "q2"]


def test_question_prompts_ask_for_pick_one_questions_without_engineering_terms():
    from app.prompts.answers import ANSWERS_PROMPT
    from app.prompts.extraction import EXTRACTION_SYSTEM
    from app.prompts.questions import QUESTIONS_PROMPT
    from app.prompts.regenerate import REGENERATE_PROMPT
    from app.prompts.topics import REVISION_PROMPT, TOPICS_PROMPT

    prompts = [
        ANSWERS_PROMPT,
        EXTRACTION_SYSTEM,
        QUESTIONS_PROMPT,
        REGENERATE_PROMPT,
        TOPICS_PROMPT,
        REVISION_PROMPT,
    ]

    for prompt in prompts:
        for word in ("debug", "software", "engineer", "code", "technical", "technology"):
            assert word not in prompt.lower(), word

    assert "multiple-choice" in QUESTIONS_PROMPT
    assert "multiple-choice" in REGENERATE_PROMPT
    assert "3-5 sentences" not in ANSWERS_PROMPT


def test_worker_skips_a_generation_cancelled_while_queued(monkeypatch):
    import asyncio
    import uuid

    from app.models.generation import Generation
    from app.storage import generations
    from app.workers import generation as worker

    started = []

    async def get(_generation_id):
        return Generation(id=uuid.uuid4(), status="cancelled", kind="preparation")

    async def run_pipeline(*args):
        started.append(args)

    monkeypatch.setattr(generations, "get", get)
    monkeypatch.setattr(worker, "run_pipeline", run_pipeline)

    asyncio.run(worker.run_generation({"graph": None}, str(uuid.uuid4())))

    assert started == []
