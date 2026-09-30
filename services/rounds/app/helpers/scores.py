from app.constants.rounds import CERTIFICATE_MIN_SCORE, Mode, RoundStatus


def current_score(scores: list[int]) -> int | None:
    """Average over answered questions; for multiple choice that is correct / answered x 100."""
    if not scores:
        return None

    return round(sum(scores) / len(scores))


def candidate_progress(scores: list[int], total: int) -> tuple[int, int | None]:
    """Share of questions answered, and the average grade of those answers."""
    if not total:
        return 0, None

    return round(len(scores) / total * 100), current_score(scores)


def interview_finished(statuses: list[str]) -> bool:
    """True once the candidate has finished every topic session."""
    return bool(statuses) and all(status == RoundStatus.FINISHED for status in statuses)


def final_score(mode: str, scores: list[int], total: int) -> int:
    """Open answer: average grade. Multiple choice: correct / total x 100."""
    if mode == Mode.CHOICE:
        # Choice scores are 100 (correct) or 0, so this is correct / total x 100.
        return round(sum(scores) / total) if total else 0

    return current_score(scores) or 0


def earns_certificate(mode: str, answered: int, total: int, coverage: int | None) -> bool:
    """`coverage` is the topic-wide average, None until every topic question has an answer."""
    return (
        mode == Mode.OPEN
        and answered == total
        and coverage is not None
        and coverage >= CERTIFICATE_MIN_SCORE
    )


def clamp_score(score: int) -> int:
    return max(0, min(100, score))
