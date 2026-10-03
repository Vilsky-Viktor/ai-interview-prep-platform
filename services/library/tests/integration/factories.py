import uuid

from prepza_common.sets import PreparationIn

from app.storage import preparations

DIMENSIONS = 256


def direction(*values: float) -> list[float]:
    """A unit vector of the embedding's size, pointing along `values`."""
    length = sum(value * value for value in values) ** 0.5

    return [value / length for value in values] + [0.0] * (DIMENSIONS - len(values))


async def preparation(
    title="Backend",
    topic="Python",
    level="mid",
    embedding=None,
    public=True,
    questions=3,
    language="en",
    owner="owner",
):
    set_id = await preparations.create(
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
                        "title": topic,
                        "subtopics": [],
                        "embedding": embedding,
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
                ],
            }
        )
    )

    if public:
        await preparations.set_visibility(set_id, "public")

    return set_id


async def question_ids(set_id):
    content = await preparations.get_content(set_id)

    return [question.id for topic in content.topics for question in topic.questions]
