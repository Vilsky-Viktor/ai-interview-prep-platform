from app.models.state import State


def collect_results(state: State) -> dict:
    """Barrier node: assembles questions, answers and options per topic."""
    topic_questions = state.get("topic_questions", [])
    final = []

    for ti, topic in enumerate(state["topics"]):
        questions = topic_questions[ti] if ti < len(topic_questions) else []
        answers = [""] * len(questions)
        answer_options: list[list[dict]] = [[] for _ in questions]

        for entry in state.get("answer_pool", []):
            if entry["topic_index"] != ti:
                continue

            for k, answer in enumerate(entry["answers"]):
                answers[entry["start"] + k] = answer

            for k, options in enumerate(entry["options"]):
                answer_options[entry["start"] + k] = options

        final.append(
            {
                "topic": topic["main_topic"],
                "subtopics": topic["subtopics"],
                "questions": questions,
                "answers": answers,
                "answer_options": answer_options,
            }
        )

    return {"final": final}
