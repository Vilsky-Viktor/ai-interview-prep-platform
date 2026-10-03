import operator
from typing import Annotated

from typing_extensions import TypedDict


class Topic(TypedDict):
    main_topic: str
    subtopics: list[str]


class QuestionTask(TypedDict):
    """Payload for one parallel generate_questions branch: one call for a topic's subtopic."""

    topic_index: int
    topic: str
    # The branch's place within its topic, so merging keeps a stable order.
    subtopic_index: int
    subtopic: str
    count: int
    level: str
    # Questions the topic already has, reused from other preparations.
    existing: list[str]
    # Which angle this call mostly asks about.
    focus: str
    language: str


class AnswerTask(TypedDict):
    """Questions that need options: a re-generated question, or new options for one."""

    topic_index: int
    topic: str
    start: int
    questions: list[str]
    level: str
    language: str


class State(TypedDict):
    input_text: str
    # The code of the language content is written in (prepza_common.constants.LANGUAGES).
    language: str
    title: str
    requirements: list[str]
    level: str
    topics: list[Topic]
    approved: bool
    # Free-text instructions from the reviewer; empty means approved.
    feedback: str
    # Parallel branches append here; operator.add merges the lists.
    question_pool: Annotated[list[dict], operator.add]
    # Merged {"text", "options"} per topic, indexed by topic index.
    topic_questions: list[list[dict]]
    # Per topic, in the topic order: its embedding, and questions reused as they are.
    topic_embeddings: list[list[float]]
    reused: list[list[dict]]
    final: list[dict]
