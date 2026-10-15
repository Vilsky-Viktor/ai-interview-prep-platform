from fastapi import APIRouter

from app.constants.events import (
    CANDIDATE_EXPIRED,
    CANDIDATE_FINISHED,
    CANDIDATE_REMOVED,
    CANDIDATE_STARTED,
    CANDIDATE_UNDELIVERED,
    INTERVIEW_READY,
    TEST_EVENT,
)
from app.schemas.public import CandidateEvent, InterviewEvent, RemovedEvent, TestEvent

# The events a web hook gets, for the reference only (main.py passes them to the app). Each
# request body is a JSON object with the event's `id`, its `type`, `occurred_at` and `data`,
# described with each.
webhooks = APIRouter()


@webhooks.post(CANDIDATE_FINISHED, summary="A candidate finished")
def candidate_finished(event: CandidateEvent) -> None:
    """Sent when a candidate finishes one of your interviews, with their results."""


@webhooks.post(CANDIDATE_STARTED, summary="A candidate started")
def candidate_started(event: CandidateEvent) -> None:
    """Sent when a candidate starts one of your interviews."""


@webhooks.post(CANDIDATE_UNDELIVERED, summary="An invitation wasn't delivered")
def candidate_undelivered(event: CandidateEvent) -> None:
    """Sent when a candidate's invitation email bounces. Send them their `invite_url` another
    way, or invite them again with another address."""


@webhooks.post(CANDIDATE_EXPIRED, summary="An invitation expired")
def candidate_expired(event: CandidateEvent) -> None:
    """Sent when a candidate's invitation expires unused, 30 days after it was last sent.
    Inviting them again revives it."""


@webhooks.post(CANDIDATE_REMOVED, summary="A candidate was removed")
def candidate_removed(event: RemovedEvent) -> None:
    """Sent when a candidate is removed from one of your interviews (revoked, or with the
    interview deleted). prepza no longer has their results; delete what you keep of them if
    you no longer need it."""


@webhooks.post(INTERVIEW_READY, summary="An interview is ready")
def interview_ready(event: InterviewEvent) -> None:
    """Sent when an interview's questions are ready, so candidates can be invited."""


@webhooks.post(TEST_EVENT, summary="A test")
def test(event: TestEvent) -> None:
    """Sent only when an owner or admin selects "send test event" on the API page, to check
    the endpoint and its signature check."""
