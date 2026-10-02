from uuid import UUID

from prepza_common.sets import PreparationIn, QuestionIn, TopicIn

from app.config.settings import settings


def build_preparation(
    generation_id: UUID, owner_uid: str, source_text: str, values: dict
) -> PreparationIn:
    """Turn the final graph state into the library payload.

    Questions without options are skipped; the spare ones after them fill the topic up to its count.
    """
    topics = []
    embeddings = values.get("topic_embeddings") or []

    for index, item in enumerate(values["final"]):
        questions = [
            QuestionIn(text=text, options=options)
            for text, options in zip(item["questions"], item["answer_options"])
            if options
        ]
        topics.append(
            TopicIn(
                title=item["topic"],
                subtopics=item["subtopics"],
                questions=questions[: settings.questions_per_topic],
                embedding=embeddings[index] if embeddings else None,
            )
        )

    return PreparationIn(
        generation_id=generation_id,
        owner_uid=owner_uid,
        source_text=source_text,
        title=values["title"],
        level=values["level"],
        requirements=values["requirements"],
        topics=topics,
    )
