def candidate_key(interview_id, email: str) -> str:
    """Names the credits billing sets aside for one candidate of one interview."""
    return f"{interview_id}:{email.lower()}"


def by_grade(listed: list, totals: dict[str, dict]) -> list:
    """Best grade first; candidates without a grade yet last. Ties keep their order, which is
    newest first."""

    def key(invite):
        grade = (totals.get(str(invite.id)) or {}).get("grade")

        return (grade is None, -(grade or 0))

    return sorted(listed, key=key)
