from pydantic import BaseModel

from app.schemas.rounds import NextQuestion
from app.schemas.sessions import SessionOut, SessionTopicOut


class InterviewStep(BaseModel):
    """Where a candidate's interview stands: the section on screen and its waiting question,
    every section, and whether the whole interview is finished."""

    session: SessionOut
    question: NextQuestion | None
    topics: list[SessionTopicOut]
    done: bool
