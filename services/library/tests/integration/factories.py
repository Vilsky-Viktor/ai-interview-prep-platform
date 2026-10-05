import uuid

from prepza_common.sets import PreparationIn

from app.storage import preparations, templates

DIMENSIONS = 256


def direction(*values: float) -> list[float]:
    """A unit vector of the embedding's size, pointing along `values`."""
    length = sum(value * value for value in values) ** 0.5

    return [value / length for value in values] + [0.0] * (DIMENSIONS - len(values))


async def interview(
    title="Backend",
    topic="Python",
    subtopics=(),
    level="mid",
    embedding=None,
    questions=3,
    language="en",
    owner="company-1",
    template=False,
    topic_embeddings=None,
):
    """A company's test set, or a template, with one topic of `questions` questions, or one
    topic per embedding in `topic_embeddings`."""
    create = templates.create_template if template else preparations.create_interview

    return await create(
        PreparationIn.model_validate(
            {
                "generation_id": str(uuid.uuid4()),
                "owner_uid": owner,
                "source_text": "job text",
                "title": title,
                "level": level,
                "language": language,
                "requirements": [],
                "topics": [
                    {
                        "title": f"{topic} {number}" if topic_embeddings else topic,
                        "subtopics": list(subtopics),
                        "embedding": topic_embedding,
                        "questions": [
                            {
                                "text": f"{title} question {index}?",
                                "options": [
                                    {"answer": "right", "correct": True},
                                    {"answer": "wrong", "correct": False},
                                ],
                            }
                            for index in range(questions)
                        ],
                    }
                    for number, topic_embedding in enumerate(topic_embeddings or [embedding])
                ],
            }
        )
    )


async def question_ids(set_id):
    content = await preparations.get_content(set_id)

    return [question.id for topic in content.topics for question in topic.questions]
