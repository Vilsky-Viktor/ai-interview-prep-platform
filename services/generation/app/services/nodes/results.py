from app.models.state import State
from app.services.nodes.questions import reused_questions


def collect_results(state: State) -> dict:
    """Barrier node: each topic's questions and their options, reused ones first."""
    topic_questions = state.get("topic_questions", [])
    final = []

    for ti, topic in enumerate(state["topics"]):
        questions = reused_questions(state, ti) + (
            topic_questions[ti] if ti < len(topic_questions) else []
        )
        final.append(
            {
                "topic": topic["main_topic"],
                "subtopics": topic["subtopics"],
                "questions": [question["text"] for question in questions],
                "answer_options": [question["options"] for question in questions],
            }
        )

    return {"final": final}
