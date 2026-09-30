import math

from langchain_core.messages import HumanMessage
from langgraph.types import Send

from app.config.settings import settings
from app.constants.generation import QUESTION_OVERSAMPLE
from app.helpers.prompts import company_block
from app.helpers.questions import merge_buckets
from app.integrations import llm
from app.models.state import QuestionTask, State
from app.prompts.questions import QUESTIONS_PROMPT
from app.schemas.questions import QuestionList


def fan_out_questions(state: State):
    """Conditional edge: one branch per (topic, subtopic)."""
    sends = []

    for ti, topic in enumerate(state["topics"]):
        subtopics = topic["subtopics"] or [topic["main_topic"]]
        per_subtopic = math.ceil(
            settings.questions_per_topic * QUESTION_OVERSAMPLE / len(subtopics)
        )

        for si, subtopic in enumerate(subtopics):
            task: QuestionTask = {
                "topic_index": ti,
                "topic": topic["main_topic"],
                "subtopic_index": si,
                "subtopic": subtopic,
                "count": per_subtopic,
                "level": state["level"],
                "company_description": state.get("company_description", ""),
            }
            sends.append(Send("generate_questions", task))

    return sends or "collect_results"


async def generate_questions(task: QuestionTask) -> dict:
    structured_llm = llm.get_question_llm().with_structured_output(QuestionList)
    prompt = QUESTIONS_PROMPT.format(
        company_block=company_block(task["company_description"]),
        level=task["level"],
        topic=task["topic"],
        subtopic=task["subtopic"],
        count=task["count"],
    )
    result: QuestionList = await structured_llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "question_pool": [
            {
                "topic_index": task["topic_index"],
                "subtopic_index": task["subtopic_index"],
                "questions": result.questions,
            }
        ]
    }


def merge_questions(state: State) -> dict:
    """Barrier node: runs after all generate_questions branches finish."""
    topic_questions: list[list[str]] = []

    for ti, topic in enumerate(state["topics"]):
        buckets: list[list[str]] = [[] for _ in range(len(topic["subtopics"]) or 1)]

        for entry in state.get("question_pool", []):
            if entry["topic_index"] == ti:
                buckets[entry["subtopic_index"]] = entry["questions"]

        topic_questions.append(merge_buckets(buckets, settings.questions_per_topic))

    return {"topic_questions": topic_questions}
