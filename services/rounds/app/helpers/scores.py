from app.constants.integrity import FAST_ANSWER_SECONDS, IntegritySignal
from app.constants.rounds import RoundStatus


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


def signal_counts(topics: list) -> dict[str, int]:
    """A candidate's integrity signals over every section: page leaves, copy attempts, and
    answers picked faster than FAST_ANSWER_SECONDS."""
    kinds = [signal.kind for topic in topics for signal in topic.signals]
    answers = [answer for topic in topics for answer in topic.answers]

    return {
        "tab_leaves": kinds.count(IntegritySignal.TAB_LEAVE),
        "copies": kinds.count(IntegritySignal.COPY),
        "fast_answers": sum(
            1
            for answer in answers
            if answer.option_index is not None
            and answer.seconds is not None
            and answer.seconds < FAST_ANSWER_SECONDS
        ),
    }


def final_score(scores: list[int], total: int) -> int:
    """Percent correct over every question of the session; unanswered ones count as wrong."""
    return round(sum(scores) / total) if total else 0


def scored(row) -> dict:
    """The session.scored event of a finished section: its score, and for each question the
    candidate saw, whether they got it right or ran out of time."""
    texts = {question["id"]: question["text"] for question in row.questions}

    return {
        "final_score": row.final_score,
        "answers": [
            {
                "question_id": str(answer.question_id),
                "question_text": texts.get(str(answer.question_id), ""),
                "correct": answer.correct,
                "timed_out": answer.option_index is None,
            }
            for answer in row.answers
        ],
    }
