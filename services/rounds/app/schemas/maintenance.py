from pydantic import BaseModel


class RunningOut(BaseModel):
    running: int
