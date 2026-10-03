from datetime import datetime
from typing import Annotated
from uuid import UUID

from prepza_common.constants import DEFAULT_LANGUAGE
from prepza_common.user import Language
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.constants.generation import (
    GOAL_PREVIEW_LENGTH,
    MAX_GOAL_LENGTH,
    MAX_SUBTOPICS,
    MAX_TOPIC_NAME_LENGTH,
    MAX_TOPICS,
)
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status


class InterviewGenerationCreate(BaseModel):
    """From companies, once it has checked the user belongs to the company."""

    text: str = Field(min_length=1, max_length=MAX_GOAL_LENGTH)
    company_id: UUID
    owner_uid: str
    # The recruiter's language, which the interview is written in.
    language: Language = DEFAULT_LANGUAGE


class GenerationCreate(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_GOAL_LENGTH)
    kind: GenerationKind = GenerationKind.PREPARATION
    company_id: UUID | None = None

    @model_validator(mode="after")
    def interview_needs_company(self):
        if self.kind == GenerationKind.INTERVIEW and self.company_id is None:
            raise ValueError("company_id is required for an interview")

        if self.kind == GenerationKind.PREPARATION and self.company_id is not None:
            raise ValueError("company_id is only used for interviews")

        return self


TopicName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TOPIC_NAME_LENGTH)
]


class EditedTopic(BaseModel):
    main_topic: TopicName
    subtopics: list[TopicName] = Field(max_length=MAX_SUBTOPICS)


class ReviewRequest(BaseModel):
    selected: list[int] = Field(min_length=1)
    instructions: str = ""
    # Every drafted topic, in order, with the reviewer's own edits; `selected` indexes this list.
    topics: list[EditedTopic] | None = None

    @model_validator(mode="after")
    def approve_at_most_max_topics(self):
        """Without instructions the review approves the selection, which caps the topics.

        With instructions the topics are revised first, so the reviewer may ask to merge.
        """
        if not self.instructions.strip() and len(self.selected) > MAX_TOPICS:
            raise ValueError(f"Choose at most {MAX_TOPICS} topics")

        return self


class DraftTopic(BaseModel):
    main_topic: str
    subtopics: list[str]


class GenerationProgress(BaseModel):
    """What the progress screen shows; the worker's own per-topic counters stay internal."""

    done: int
    total: int
    # Missing on generations started before per-topic progress existed.
    topics: int | None = None
    topics_ready: int | None = None


class GenerationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: GenerationKind
    company_id: UUID | None
    status: Status
    topics: list[DraftTopic] | None
    progress: GenerationProgress | None
    preparation_id: UUID | None
    error: str | None
    max_topics: int = MAX_TOPICS


class GenerationSummary(BaseModel):
    """An unfinished generation in a list, with the start of the goal it was made from."""

    id: UUID
    status: Status
    preview: str
    created_at: datetime

    @classmethod
    def of(cls, generation) -> "GenerationSummary":
        text = " ".join(generation.text.split())
        preview = text[:GOAL_PREVIEW_LENGTH] + ("…" if len(text) > GOAL_PREVIEW_LENGTH else "")

        return cls(
            id=generation.id,
            status=generation.status,
            preview=preview,
            created_at=generation.created_at,
        )
