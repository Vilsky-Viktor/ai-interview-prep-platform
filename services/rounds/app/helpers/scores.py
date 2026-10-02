from app.constants.rounds import CERTIFICATE_MIN_SCORE, RoundStatus


def current_score(scores: list[int]) -> int | None:
    """Percent correct over the answered questions."""
    if not scores:
        return None

    return round(sum(scores) / len(scores))


def candidate_progress(scores: list[int], total: int) -> tuple[int, int | None]:
    """Share of questions answered, and the percent correct of those answers."""
    if not total:
        return 0, None

    return round(len(scores) / total * 100), current_score(scores)


def interview_finished(statuses: list[str]) -> bool:
    """True once the candidate has finished every topic session."""
    return bool(statuses) and all(status == RoundStatus.FINISHED for status in statuses)


def final_score(scores: list[int], total: int) -> int:
    """Percent correct over every question of the round; unanswered ones count as wrong."""
    return round(sum(scores) / total) if total else 0


def earns_certificate(coverage: int | None) -> bool:
    """`coverage` is the topic-wide score, None until every topic question has an answer."""
    return coverage is not None and coverage >= CERTIFICATE_MIN_SCORE


def score_passed(score: int | None) -> bool | None:
    """Whether a score reaches the pass mark; None while there is no score."""
    return None if score is None else score >= CERTIFICATE_MIN_SCORE
