from app.config.settings import settings
from app.constants.generation import FILL_ATTEMPTS, FILL_SPARE_QUESTIONS
from app.helpers.questions import normalize
from app.models.state import State
from app.services.dedupe import distinct_by_meaning
from app.services.nodes.questions import generate_questions


class TopicShortError(Exception):
    """A topic still lacks questions after every attempt; the generation fails and can retry."""


def usable(item: dict) -> int:
    return sum(1 for options in item["answer_options"] if options)


async def new_questions(item: dict, missing: int, state: State) -> list[dict]:
    """Questions with options on the topic, different from every one it already has, in words
    and in meaning, as the pipeline's own are."""
    result = await generate_questions(
        {
            "topic_index": 0,
            "topic": item["topic"],
            "subtopic_index": 0,
            "subtopic": ", ".join(item["subtopics"]) or item["topic"],
            "count": missing + FILL_SPARE_QUESTIONS,
            "kind": state.get("kind"),
            "level": state["level"],
            "free_kit": state.get("free_kit", False),
            "existing": item["questions"],
            "language": state.get("language"),
        }
    )
    taken = {normalize(text) for text in item["questions"]}
    fresh = []

    for question in result["question_pool"][0]["questions"]:
        if normalize(question["text"]) not in taken:
            taken.add(normalize(question["text"]))
            fresh.append(question)

    existing = len(item["questions"])
    kept = await distinct_by_meaning(
        item["questions"] + [question["text"] for question in fresh], keep_first=existing
    )

    return [fresh[index - existing] for index in kept[existing:]]


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

            # The spares asked for beyond what's missing are left out.
            for question in (await new_questions(item, missing, state))[:missing]:
                item["questions"].append(question["text"])
                item["answer_options"].append(question["options"])

        if usable(item) < settings.questions_per_topic:
            raise TopicShortError(f"Topic {item['topic']!r} has only {usable(item)} questions")

    return {"final": final}
