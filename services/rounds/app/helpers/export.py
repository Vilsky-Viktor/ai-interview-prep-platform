def answer_export(questions: list[dict], answer) -> dict:
    """An answer with its question and the option picked, readable without the ids.

    A timed question that ran out has no option picked. The correct option isn't included: in
    an interview it isn't the candidate's to see.
    """
    question = next((item for item in questions if item["id"] == str(answer.question_id)), None)
    picked = None

    if question and answer.option_index is not None:
        picked = question["options"][answer.option_index]["answer"]

    return {
        "question": question["text"] if question else None,
        "your_answer": picked,
        "correct": answer.correct,
        "at": answer.created_at,
    }
