import uuid

from app.constants.invites import SIGNAL_KEYS
from app.schemas.invites import CandidateOut


def candidate_key(interview_id, email: str) -> str:
    """Names the credits billing set aside for one candidate of one interview, on invites made
    before each had its own key."""
    return f"{interview_id}:{email.lower()}"


def new_hold_key(interview_id, email: str) -> str:
    """A new invite's own key for its credits: a candidate invited again after their invite was
    removed gets a new one, so they're charged again (billing keeps a charged key charged)."""
    return f"{candidate_key(interview_id, email)}:{uuid.uuid4().hex}"


def hold_key(interview_id, email: str, stored: str | None) -> str:
    """The key of an invite's credits: its own, or candidate_key on older invites."""
    return stored or candidate_key(interview_id, email)


def passed(totals: dict, pass_mark: int) -> bool | None:
    """Whether a finished candidate reached the pass mark; None before they finish."""
    if not totals.get("finished") or totals.get("grade") is None:
        return None

    return totals["grade"] >= pass_mark


def finished_result(interview, invite_id, grade: int | None, flagged: bool) -> dict:
    """The candidate.finished event: what ats writes back to the ATS that sent the candidate."""
    return {
        "candidate_invite_id": str(invite_id),
        "interview_id": str(interview.id),
        "company_id": str(interview.company_id),
        "title": interview.title or "",
        "grade": grade,
        "passed": grade is not None and grade >= interview.pass_mark,
        "flagged": flagged,
    }


def section_passed(section: dict, pass_mark: int) -> bool | None:
    """Whether a finished section's score reached the pass mark; None while it's still going."""
    if section.get("status") != "finished" or section.get("final_score") is None:
        return None

    return section["final_score"] >= pass_mark


def flagged(totals: dict) -> bool:
    """True when the candidate has any integrity signal."""
    return any(totals.get(key) for key in SIGNAL_KEYS)


def stored_results(totals: dict) -> tuple[int | None, bool]:
    """What the invite keeps of a finished candidate's results: their grade and integrity flag."""
    return totals.get("grade"), flagged(totals)


def candidate_out(invite, totals: dict, interview) -> CandidateOut:
    """A candidate row: the invite, with their results from rounds."""
    return CandidateOut(
        id=invite.id,
        email=invite.email,
        status=invite.status,
        progress=totals.get("progress", 0),
        grade=totals.get("grade"),
        passed=passed(totals, interview.pass_mark),
        **{key: totals.get(key, 0) for key in SIGNAL_KEYS},
        created_at=invite.created_at,
    )


def candidate_seconds(question_seconds: int, extra_time: int | None) -> int:
    """Each question's time for a candidate, with any extra time they were given."""
    return round(question_seconds * (100 + (extra_time or 0)) / 100)
