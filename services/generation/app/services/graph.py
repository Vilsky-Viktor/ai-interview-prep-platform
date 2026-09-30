from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.models.state import State
from app.services.nodes.answers import fan_out_answers, generate_answers
from app.services.nodes.extraction import extract_info, needs_company_search, search_company
from app.services.nodes.questions import generate_questions, merge_questions
from app.services.nodes.results import collect_results
from app.services.nodes.topics import (
    generate_topics,
    human_review,
    review_router,
    revise_topics,
)


def build_graph(checkpointer: BaseCheckpointSaver):
    """job text -> extraction -> (company lookup) -> topics -> human review loop ->
    parallel questions -> merge -> parallel answers + options -> final results."""
    graph = StateGraph(State)
    graph.add_node("extract_info", extract_info)
    graph.add_node("search_company", search_company)
    graph.add_node("generate_topics", generate_topics)
    graph.add_node("human_review", human_review)
    graph.add_node("revise_topics", revise_topics)
    graph.add_node("generate_questions", generate_questions)
    graph.add_node("merge_questions", merge_questions)
    graph.add_node("generate_answers", generate_answers)
    graph.add_node("collect_results", collect_results)

    graph.add_edge(START, "extract_info")
    graph.add_conditional_edges(
        "extract_info",
        needs_company_search,
        {"search_company": "search_company", "generate_topics": "generate_topics"},
    )
    graph.add_edge("search_company", "generate_topics")
    graph.add_edge("generate_topics", "human_review")
    # Revise loop, or stage 1 fan-out.
    graph.add_conditional_edges("human_review", review_router)
    graph.add_edge("revise_topics", "human_review")
    # Barrier: merge waits for every question branch.
    graph.add_edge("generate_questions", "merge_questions")
    # Stage 2 fan-out.
    graph.add_conditional_edges("merge_questions", fan_out_answers)
    # Barrier: results wait for every answer branch.
    graph.add_edge("generate_answers", "collect_results")
    graph.add_edge("collect_results", END)

    return graph.compile(checkpointer=checkpointer)
