from pydantic import BaseModel, Field


class Grade(BaseModel):
    score: int = Field(
        description="How correctly and completely the answer covers the question, 0-100."
    )
    feedback: str = Field(
        description="1-3 sentences to the candidate: what was right and what was missing or wrong."
    )
