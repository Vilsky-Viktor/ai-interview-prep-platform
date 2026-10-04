import logging
import math

from langchain_core.messages import HumanMessage
from langgraph.types import Send
from openai import LengthFinishReasonError

from app.config.settings import settings
from app.constants.generation import (
    DISTRACTORS,
    MAX_OPTION_CHARS,
    QUESTION_ATTEMPTS,
    QUESTION_FOCUSES,
    QUESTION_OVERSAMPLE,
)
from app.helpers.prompts import bullet_list, language_name
from app.helpers.questions import (
    build_options,
    merge_buckets,
    normalize,
    question_calls,
    split_count,
    with_example,
)
from app.integrations import llm
from app.models.state import QuestionTask, State
from app.prompts.questions import QUESTIONS_PROMPT
from app.schemas.questions import QuestionItemList
from app.services.dedupe import distinct_by_meaning

logger = logging.getLogger(__name__)


def reused_questions(state: State, topic_index: int) -> list[dict]:
    reused = state.get("reused") or []

    return reused[topic_index] if reused else []


def focus_for(call: int, calls: int) -> str:
    if calls == 1:
        return "a mix of " + "; ".join(QUESTION_FOCUSES)

    return QUESTION_FOCUSES[call % len(QUESTION_FOCUSES)]


def fan_out_questions(state: State):
    """Conditional edge: one branch per call of each (topic, subtopic), for what reuse left."""
    sends = []

    for ti, topic in enumerate(state["topics"]):
        subtopics = topic["subtopics"] or [topic["main_topic"]]
        reused = reused_questions(state, ti)
        needed = settings.questions_per_topic - len(reused)
        per_subtopic = math.ceil(needed * QUESTION_OVERSAMPLE / len(subtopics))
        calls = question_calls(len(subtopics))
        bucket = 0

        for si, subtopic in enumerate(subtopics):
            for call, count in enumerate(split_count(per_subtopic, calls)):
                task: QuestionTask = {
                    "topic_index": ti,
                    "topic": topic["main_topic"],
                    "subtopic_index": bucket,
                    "subtopic": subtopic,
                    "count": count,
                    "kind": state.get("kind"),
                    "level": state["level"],
                    "free_kit": state.get("free_kit", False),
                    "existing": [question["text"] for question in reused],
                    "focus": focus_for(call, calls),
                    "language": state.get("language"),
                }
                sends.append(Send("generate_questions", task))
                bucket += 1

    return sends or "collect_results"


async def generate_questions(task: QuestionTask) -> dict:
    """Questions with their options in one call; ambiguous or incomplete ones are dropped."""
    structured_llm = llm.get_generation_llm(
        task.get("kind"), task["level"], task.get("free_kit", False)
    ).with_structured_output(QuestionItemList)
    prompt = QUESTIONS_PROMPT.format(
        level=task["level"],
        topic=task["topic"],
        subtopic=task["subtopic"],
        focus=task.get("focus") or focus_for(0, 1),
        count=task["count"],
        distractors=DISTRACTORS,
        max_chars=MAX_OPTION_CHARS,
        existing=bullet_list(task.get("existing", [])) or "None",
        language=language_name(task.get("language")),
    )
    items = []

    for attempt in range(1, QUESTION_ATTEMPTS + 1):
        try:
            result: QuestionItemList = await structured_llm.ainvoke([HumanMessage(content=prompt)])
        except LengthFinishReasonError:
            # The model looped until the output cap; ask again.
            logger.warning("Questions for %r ran too long (attempt %d)", task["subtopic"], attempt)

            continue

        items = result.items

        break

    questions = []

    for item in items:
        text = with_example(item.question, item.example)
        options = None if item.ambiguous else build_options(item.correct_option, item.distractors)

        if text and options:
            questions.append({"text": text, "options": options})

    # If every attempt ran too long, this call adds nothing; fill_topics makes up for it.
    return {
        "question_pool": [
            {
                "topic_index": task["topic_index"],
                "subtopic_index": task["subtopic_index"],
                "questions": questions[: task["count"]],
            }
        ]
    }


async def merge_questions(state: State) -> dict:
    """Barrier node: per topic, one list of distinct questions, up to what reuse left to fill."""
    topic_questions: list[list[dict]] = []

    for ti in range(len(state["topics"])):
        entries = [entry for entry in state.get("question_pool", []) if entry["topic_index"] == ti]
        entries.sort(key=lambda entry: entry["subtopic_index"])
        reused = reused_questions(state, ti)
        taken = {normalize(question["text"]) for question in reused}
        merged = [
            question
            for question in merge_buckets([entry["questions"] for entry in entries])
            if normalize(question["text"]) not in taken
        ]
        texts = [question["text"] for question in reused + merged]
        kept = await distinct_by_meaning(texts, keep_first=len(reused))
        distinct = [merged[index - len(reused)] for index in kept if index >= len(reused)]
        topic_questions.append(distinct[: settings.questions_per_topic - len(reused)])

    return {"topic_questions": topic_questions}
