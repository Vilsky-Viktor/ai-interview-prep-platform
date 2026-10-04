import json

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import interrupt

from app.constants.generation import MAX_TOPIC_NAME_LENGTH, MAX_TOPICS, TOPIC_ATTEMPTS
from app.helpers.prompts import bullet_list, language_name
from app.helpers.topics import fit_topics
from app.integrations import llm
from app.models.state import State
from app.prompts.topics import REVISION_PROMPT, TOO_MANY_TOPICS, TOPICS_PROMPT
from app.schemas.topics import TopicList
from app.storage import draft_cache


async def plan_topics(prompt: str, model) -> list[dict]:
    """Ask for topics; when the model goes over the limit, send the list back to merge."""
    structured_llm = model.with_structured_output(TopicList)
    messages = [HumanMessage(content=prompt)]

    for _ in range(TOPIC_ATTEMPTS):
        result: TopicList = await structured_llm.ainvoke(messages)
        topics = [topic.model_dump() for topic in result.topics]

        if len(topics) <= MAX_TOPICS:
            break

        messages += [
            AIMessage(content=json.dumps(topics, ensure_ascii=False)),
            HumanMessage(content=TOO_MANY_TOPICS.format(count=len(topics), max_topics=MAX_TOPICS)),
        ]

    return fit_topics(topics)


async def generate_topics(state: State) -> dict:
    """Drafts topics; the same level and requirements reuse their earlier draft."""
    prompt = TOPICS_PROMPT.format(
        level=state["level"],
        requirements=bullet_list(state["requirements"]),
        max_topics=MAX_TOPICS,
        max_name=MAX_TOPIC_NAME_LENGTH,
        language=language_name(state.get("language")),
    )
    model = llm.get_generation_llm(state.get("kind"), state["level"])
    topics = await draft_cache.get("topics", prompt, model)

    if topics is None:
        topics = await plan_topics(prompt, model)
        await draft_cache.put("topics", prompt, topics, model)

    # Drafts cached before the names had a limit are fitted too.
    return {"topics": fit_topics(topics)}


def human_review(state: State) -> dict:
    # Pauses the graph until the API resumes it with {"selected": [topic indices to keep],
    # "instructions": "free text or empty", "topics": [every topic, edited by hand] or null}.
    response = interrupt({"topics": state["topics"]}) or {}
    keep = set(response.get("selected") or [])
    edited = response.get("topics")
    # Edits made by hand need no model call; an edited list must match the drafted one.
    topics = edited if edited and len(edited) == len(state["topics"]) else state["topics"]
    kept = [topic for index, topic in enumerate(topics) if index in keep]
    instructions = (response.get("instructions") or "").strip()

    # Empty instructions mean approved; otherwise the topics go to revise_topics.
    return {"topics": kept, "feedback": instructions, "approved": not instructions}


async def revise_topics(state: State) -> dict:
    """Apply the reviewer's free-text instructions to the topics kept in the checkboxes."""
    prompt = REVISION_PROMPT.format(
        level=state["level"],
        requirements=bullet_list(state["requirements"]),
        current=json.dumps(state["topics"], indent=2, ensure_ascii=False),
        feedback=state["feedback"],
        max_topics=MAX_TOPICS,
        max_name=MAX_TOPIC_NAME_LENGTH,
        language=language_name(state.get("language")),
    )

    return {
        "topics": await plan_topics(
            prompt, llm.get_generation_llm(state.get("kind"), state["level"])
        ),
        "feedback": "",
        "approved": False,
    }


def review_router(state: State):
    """Conditional edge after human_review: revise again, or look for questions to reuse."""
    if not state.get("approved"):
        return "revise_topics"

    return "find_reused"
