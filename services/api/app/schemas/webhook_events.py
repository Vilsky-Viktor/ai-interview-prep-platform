from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.public import CandidateEvent, InterviewEvent, RemovedEvent, TestEvent


class WebhookEvent(BaseModel):
    """What every web hook request's body holds, besides the event's `data`."""

    id: str = Field(description="The event's id: the same when it's sent again")
    type: str = Field(description="The event's type, such as candidate.finished")
    occurred_at: datetime = Field(
        description="When the change happened, to put events in order: a retried one can "
        "arrive after a later one"
    )


class CandidateWebhook(WebhookEvent):
    data: CandidateEvent


class RemovedWebhook(WebhookEvent):
    data: RemovedEvent


class InterviewWebhook(WebhookEvent):
    data: InterviewEvent


class TestWebhook(WebhookEvent):
    data: TestEvent
