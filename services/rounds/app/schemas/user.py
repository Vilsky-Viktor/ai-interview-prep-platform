from pydantic import BaseModel


class User(BaseModel):
    uid: str
    email: str
    email_verified: bool
    name: str | None = None
