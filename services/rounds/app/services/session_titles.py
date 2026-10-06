from app.helpers.sessions import session_out
from app.integrations import library
from app.models.sessions import Session
from app.schemas.sessions import SessionOut


async def session_out_titled(row: Session) -> SessionOut:
    found = await library.get_set(row.interview_set_id)

    if found is None:
        return session_out(row)

    return session_out(row, found["title"], found.get("language"))
