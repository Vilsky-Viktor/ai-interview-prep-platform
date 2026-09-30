from app.helpers.rounds import next_question
from app.helpers.scores import current_score
from app.integrations import library
from app.models.sessions import Session
from app.schemas.sessions import SessionOut, SessionTopicOut


def topic_out(row: Session) -> SessionTopicOut:
    return SessionTopicOut(
        id=row.id,
        topic_title=row.topic_title,
        status=row.status,
        total=len(row.questions),
        answered=len(row.answers),
    )


async def session_out_titled(row: Session) -> SessionOut:
    found = await library.get_set(row.interview_set_id)

    return session_out(row, found["title"] if found else None)


def session_out(row: Session, interview_title: str | None = None) -> SessionOut:
    scores = [answer.score for answer in row.answers]
    shown = row.share_results

    return SessionOut(
        id=row.id,
        topic_id=row.topic_id,
        topic_title=row.topic_title,
        interview_title=interview_title,
        mode=row.mode,
        share_results=row.share_results,
        status=row.status,
        total=len(row.questions),
        answered=len(row.answers),
        current_score=current_score(scores) if shown else None,
        final_score=row.final_score if shown else None,
        started_at=row.started_at,
        finished_at=row.finished_at,
    )


# Sessions use the same next-question shape as rounds.
next_session_question = next_question
