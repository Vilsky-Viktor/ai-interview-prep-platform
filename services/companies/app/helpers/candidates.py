from app.constants.invites import SIGNAL_KEYS
from app.schemas.invites import CandidateOut


def candidate_key(interview_id, email: str) -> str:
    """Names the credits billing sets aside for one candidate of one interview."""
    return f"{interview_id}:{email.lower()}"


def passed(totals: dict, pass_mark: int) -> bool | None:
    """Whether a finished candidate reached the pass mark; None before they finish."""
    if not totals.get("finished") or totals.get("grade") is None:
        return None

    return totals["grade"] >= pass_mark


def section_passed(section: dict, pass_mark: int) -> bool | None:
    """Whether a finished section's score reached the pass mark; None while it's still going."""
    if section.get("status") != "finished" or section.get("final_score") is None:
        return None

    return section["final_score"] >= pass_mark


def flagged(totals: dict) -> bool:
    """True when the candidate has any integrity signal."""
    return any(totals.get(key) for key in SIGNAL_KEYS)


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


def by_grade(listed: list, totals: dict[str, dict]) -> list:
    """Best grade first; candidates without a grade yet last. Ties keep their order, which is
    newest first."""

    def key(invite):
        grade = (totals.get(str(invite.id)) or {}).get("grade")

        return (grade is None, -(grade or 0))

    return sorted(listed, key=key)


def candidate_seconds(question_seconds: int, extra_time: int | None) -> int:
    """Each question's time for a candidate, with any extra time they were given."""
    return round(question_seconds * (100 + (extra_time or 0)) / 100)
