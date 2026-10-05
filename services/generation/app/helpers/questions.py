import math
import random
import re

from app.config.settings import settings
from app.constants.generation import (
    DISTRACTORS,
    MAX_OPTION_CHARS,
    QUESTION_BATCH_SIZE,
    QUESTION_OVERSAMPLE,
)

# A line starting with "A." or "A)" begins choices the model listed in the question itself.
LISTED_CHOICES = re.compile(r"\n\s*A[.)]\s.*", re.DOTALL)
# A Markdown fence the model put around an example itself.
EXAMPLE_FENCE = re.compile(r"^```[\w+-]*\n?|\n?```$")


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def strip_choices(question: str) -> str:
    return LISTED_CHOICES.sub("", question).strip()


def with_example(question: str, example: str | None) -> str:
    """The question as it's stored and shown: its sentences, then its example in a fenced block.
    A question that already holds a block keeps it as it is."""
    question = strip_choices(question)
    example = EXAMPLE_FENCE.sub("", (example or "").strip()).strip("\n")

    if not question or not example.strip() or "```" in question:
        return question

    return f"{question}\n```\n{example}\n```"


def merge_buckets(buckets: list[list[dict]]) -> list[dict]:
    """Round-robin across buckets of {"text", "options"}, dropping exact duplicates."""
    seen = set()
    merged: list[dict] = []

    for row in range(max((len(bucket) for bucket in buckets), default=0)):
        for bucket in buckets:
            if row < len(bucket) and normalize(bucket[row]["text"]) not in seen:
                seen.add(normalize(bucket[row]["text"]))
                merged.append(bucket[row])

    return merged


def topic_size(template: bool) -> int:
    """Questions each topic gets: more for a template than for a company's test."""
    if template:
        return settings.template_questions_per_topic

    return settings.interview_questions_per_topic


def question_calls(subtopic_count: int, size: int) -> int:
    """Calls each subtopic's questions are split into; reuse lowers their size, not their number."""
    per_subtopic = math.ceil(size * QUESTION_OVERSAMPLE / subtopic_count)

    return math.ceil(per_subtopic / QUESTION_BATCH_SIZE)


def split_count(count: int, parts: int) -> list[int]:
    """`count` spread over `parts` as evenly as possible."""
    return [count // parts + (1 if part < count % parts else 0) for part in range(parts)]


def clean_distractors(distractors: list[str], correct: str, max_chars: int) -> list[str]:
    """Strip, dedupe (case-insensitive), drop anything equal to the correct option or too long."""
    seen = {normalize(correct)}
    cleaned: list[str] = []

    for distractor in distractors:
        distractor = distractor.strip()
        key = normalize(distractor)

        if distractor and len(distractor) <= max_chars and key not in seen:
            seen.add(key)
            cleaned.append(distractor)

    return cleaned


def build_options(correct: str, distractors: list[str]) -> list[dict] | None:
    """The correct option and DISTRACTORS wrong ones, shuffled; None when they don't qualify."""
    correct = correct.strip()
    wrong = clean_distractors(distractors, correct, MAX_OPTION_CHARS)

    if not correct or len(correct) > MAX_OPTION_CHARS or len(wrong) < DISTRACTORS:
        return None

    options = [{"answer": correct, "correct": True}] + [
        {"answer": answer, "correct": False} for answer in wrong[:DISTRACTORS]
    ]
    # Avoid the correct option always being first.
    random.shuffle(options)

    return options
