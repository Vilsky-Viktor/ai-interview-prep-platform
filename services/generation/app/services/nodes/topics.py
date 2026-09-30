import json

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from app.constants.generation import MAX_TOPICS
from app.helpers.prompts import bullet_list, company_block
from app.integrations import llm
from app.models.state import State
from app.prompts.topics import REVISION_PROMPT, TOPICS_PROMPT
from app.schemas.topics import TopicList
from app.services.nodes.questions import fan_out_questions


async def generate_topics(state: State) -> dict:
    structured_llm = llm.get_llm().with_structured_output(TopicList)
    prompt = TOPICS_PROMPT.format(
        company_block=company_block(state.get("company_description", "")),
        level=state["level"],
        requirements=bullet_list(state["requirements"]),
        max_topics=MAX_TOPICS,
    )
    result: TopicList = await structured_llm.ainvoke([HumanMessage(content=prompt)])

    return {"topics": [topic.model_dump() for topic in result.topics]}


def human_review(state: State) -> dict:
    # Pauses the graph until the API resumes it with
    # {"selected": [topic indices to keep], "instructions": "free text or empty"}.
    response = interrupt({"topics": state["topics"]}) or {}
    keep = set(response.get("selected") or [])
    kept = [topic for index, topic in enumerate(state["topics"]) if index in keep]
    instructions = (response.get("instructions") or "").strip()

    # Empty instructions mean approved; otherwise the topics go to revise_topics.
    return {"topics": kept, "feedback": instructions, "approved": not instructions}


async def revise_topics(state: State) -> dict:
    """Apply the reviewer's free-text instructions to the topics kept in the checkboxes."""
    structured_llm = llm.get_llm().with_structured_output(TopicList)
    prompt = REVISION_PROMPT.format(
        level=state["level"],
        requirements=bullet_list(state["requirements"]),
        current=json.dumps(state["topics"], indent=2, ensure_ascii=False),
        feedback=state["feedback"],
        max_topics=MAX_TOPICS,
    )
    result: TopicList = await structured_llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "topics": [topic.model_dump() for topic in result.topics],
        "feedback": "",
        "approved": False,
    }


def review_router(state: State):
    """Conditional edge after human_review: revise again, or start question generation."""
    if not state.get("approved"):
        return "revise_topics"

    return fan_out_questions(state)
