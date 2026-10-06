from app.constants.rounds import RoundStatus


def interview_finished(statuses: list[str]) -> bool:
    """True once the candidate has finished every topic session."""
    return bool(statuses) and all(status == RoundStatus.FINISHED for status in statuses)


def invite_grade(answered: int, score_sum: int, total: int, finished: bool) -> dict:
    """A candidate's share of questions answered, and their grade: percent correct of the
    answers so far, or, once they finished, of every question (unanswered ones count as wrong,
    as in each section's score)."""
    if finished:
        grade = round(score_sum / total) if total else 0
    else:
        grade = round(score_sum / answered) if answered and total else None

    return {
        "progress": round(answered / total * 100) if total else 0,
        "grade": grade,
        "finished": finished,
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
