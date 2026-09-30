import operator
from typing import Annotated

from typing_extensions import TypedDict


class Topic(TypedDict):
    main_topic: str
    subtopics: list[str]


class QuestionTask(TypedDict):
    """Payload for one parallel generate_questions branch (topic x subtopic)."""

    topic_index: int
    topic: str
    subtopic_index: int
    subtopic: str
    count: int
    level: str
    company_description: str


class AnswerTask(TypedDict):
    """Payload for one parallel generate_answers branch (batch of questions)."""

    topic_index: int
    topic: str
    start: int
    questions: list[str]
    level: str
    company_description: str


class State(TypedDict):
    input_text: str
    title: str
    company_name: str
    company_description: str
    requirements: list[str]
    level: str
    topics: list[Topic]
    approved: bool
    # Free-text instructions from the reviewer; empty means approved.
    feedback: str
    # Parallel branches append here; operator.add merges the lists.
    question_pool: Annotated[list[dict], operator.add]
    # Merged questions, indexed by topic index.
    topic_questions: list[list[str]]
    answer_pool: Annotated[list[dict], operator.add]
    final: list[dict]
