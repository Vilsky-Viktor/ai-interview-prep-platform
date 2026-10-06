def rekeyed(question: dict, text: str, options: list[dict]) -> bool:
    """Moves a session's copy of a question to its corrected key, keeping the candidate's option
    order. Only when it's the same question with the same options: a rewritten one was a
    different question. True if the key moved."""
    correct = {option["answer"]: option["correct"] for option in options}

    if question["text"] != text or {option["answer"] for option in question["options"]} != set(
        correct
    ):
        return False

    moved = any(option["correct"] != correct[option["answer"]] for option in question["options"])

    for option in question["options"]:
        option["correct"] = correct[option["answer"]]

    return moved
