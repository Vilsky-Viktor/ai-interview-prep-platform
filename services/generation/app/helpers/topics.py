from app.constants.generation import MAX_TOPIC_NAME_LENGTH


def fit_name(name: str) -> str:
    """A drafted name within the review's limit: cut at the last whole word that fits, so
    approving a draft never fails on a name the model made too long."""
    name = name.strip()

    if len(name) <= MAX_TOPIC_NAME_LENGTH:
        return name

    window = name[: MAX_TOPIC_NAME_LENGTH + 1]

    # One long word has nowhere to cut, so it's cut at the limit.
    if " " not in window:
        return name[:MAX_TOPIC_NAME_LENGTH]

    return window.rsplit(" ", 1)[0].rstrip(" ,;:-–—")


def fit_topics(topics: list[dict]) -> list[dict]:
    return [
        {
            **topic,
            "main_topic": fit_name(topic["main_topic"]),
            "subtopics": [fit_name(subtopic) for subtopic in topic["subtopics"]],
        }
        for topic in topics
    ]
