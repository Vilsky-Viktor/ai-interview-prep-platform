def answer_export(questions: list[dict], answer, practice: bool) -> dict:
    """An answer with its question and the option picked, readable without the ids.

    A timed question that ran out has no option picked. Whether it was right is included only
    for practice, which is the talent's own: in a company's interview it isn't the candidate's
    to see, and across candidates it would build an answer key.
    """
    question = next((item for item in questions if item["id"] == str(answer.question_id)), None)
    picked = None

    if question and answer.option_index is not None:
        picked = question["options"][answer.option_index]["answer"]

    exported = {
        "question": question["text"] if question else None,
        "your_answer": picked,
        "at": answer.created_at,
    }

    if practice:
        exported["correct"] = answer.correct

    return exported
