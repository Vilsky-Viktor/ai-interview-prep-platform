from app.schemas.library import PreparationIn, QuestionIn, TopicIn


def build_preparation(owner_uid: str, source_text: str, values: dict) -> PreparationIn:
    """Turn the final graph state into the library payload, skipping incomplete questions."""
    topics = []

    for item in values["final"]:
        questions = [
            QuestionIn(text=text, reference_answer=answer, options=options)
            for text, answer, options in zip(
                item["questions"], item["answers"], item["answer_options"]
            )
            if answer and options
        ]
        topics.append(
            TopicIn(title=item["topic"], subtopics=item["subtopics"], questions=questions)
        )

    return PreparationIn(
        owner_uid=owner_uid,
        source_text=source_text,
        title=values["title"],
        level=values["level"],
        requirements=values["requirements"],
        topics=topics,
    )
