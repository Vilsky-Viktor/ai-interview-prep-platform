import math

from app.config.settings import settings
from app.constants.generation import FILL_ATTEMPTS, QUESTION_OVERSAMPLE
from app.helpers.questions import normalize
from app.models.state import State
from app.services.nodes.questions import generate_questions


class TopicShortError(Exception):
    """A topic still lacks questions after every attempt; the generation fails and can retry."""


def usable(item: dict) -> int:
    return sum(1 for options in item["answer_options"] if options)


async def new_questions(
    item: dict, missing: int, kind: str | None, level: str, language: str
) -> list[dict]:
    """Questions with options on the topic, different from every one it already has."""
    result = await generate_questions(
        {
            "topic_index": 0,
            "topic": item["topic"],
            "subtopic_index": 0,
            "subtopic": ", ".join(item["subtopics"]) or item["topic"],
            "count": math.ceil(missing * QUESTION_OVERSAMPLE),
            "kind": kind,
            "level": level,
            "existing": item["questions"],
            "language": language,
        }
    )
    taken = {normalize(text) for text in item["questions"]}
    fresh = []

    for question in result["question_pool"][0]["questions"]:
        if normalize(question["text"]) not in taken:
            taken.add(normalize(question["text"]))
            fresh.append(question)

    return fresh


async def fill_topics(state: State) -> dict:
    """Tops up every topic that ended below its size, so each one has exactly as many questions.

    Questions get dropped as ambiguous, and a subtopic can fail; the spares don't always cover it.
    """
    final = [
        {
            **item,
            "questions": list(item["questions"]),
            "answer_options": list(item["answer_options"]),
        }
        for item in state["final"]
    ]

    for item in final:
        for _ in range(FILL_ATTEMPTS):
            missing = settings.questions_per_topic - usable(item)

            if missing <= 0:
                break

            for question in await new_questions(
                item, missing, state.get("kind"), state["level"], state.get("language")
            ):
                item["questions"].append(question["text"])
                item["answer_options"].append(question["options"])

        if usable(item) < settings.questions_per_topic:
            raise TopicShortError(f"Topic {item['topic']!r} has only {usable(item)} questions")

    return {"final": final}
