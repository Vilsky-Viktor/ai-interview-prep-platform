from app.constants.feedback import ReportReason
from app.constants.quality import (
    DEAD_OPTION_SHARE,
    DISLIKES_TO_FLAG,
    MIN_ANSWERS,
    REPORTS_TO_FLAG,
    TOO_EASY_RATE,
    TOO_HARD_RATE,
    QualityFlag,
)


def wrong_key(options: list[dict], option_picks: dict[str, int]) -> bool:
    """A wrong option is picked more often than the one marked correct."""
    right = sum(option_picks.get(option["answer"], 0) for option in options if option["correct"])

    return any(
        option_picks.get(option["answer"], 0) > right for option in options if not option["correct"]
    )


def dead_option(options: list[dict], answers: int, option_picks: dict[str, int]) -> bool:
    return any(
        option_picks.get(option["answer"], 0) < answers * DEAD_OPTION_SHARE
        for option in options
        if not option["correct"]
    )


def flag_for(
    options: list[dict],
    answers: int,
    correct: int,
    option_picks: dict[str, int],
    reports: dict[str, int],
    likes: int,
    dislikes: int,
) -> QualityFlag | None:
    """The most serious problem the answers and feedback show, or None."""
    answered = answers >= MIN_ANSWERS

    if reports.get(ReportReason.WRONG_ANSWER, 0) >= REPORTS_TO_FLAG or (
        answered and wrong_key(options, option_picks)
    ):
        return QualityFlag.WRONG_KEY

    if (
        reports.get(ReportReason.UNCLEAR, 0) >= REPORTS_TO_FLAG
        or reports.get(ReportReason.OFF_TOPIC, 0) >= REPORTS_TO_FLAG
        or (dislikes >= DISLIKES_TO_FLAG and dislikes >= 2 * likes)
        or (answered and correct <= answers * TOO_HARD_RATE)
    ):
        return QualityFlag.REWRITE

    if answered and (
        correct >= answers * TOO_EASY_RATE or dead_option(options, answers, option_picks)
    ):
        return QualityFlag.WEAK_OPTIONS

    return None
