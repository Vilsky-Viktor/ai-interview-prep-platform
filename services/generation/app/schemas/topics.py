from pydantic import BaseModel, Field


class TopicStructure(BaseModel):
    main_topic: str = Field(description="Main topic of preparation")
    subtopics: list[str] = Field(description="Subtopics for preparation")


class TopicList(BaseModel):
    topics: list[TopicStructure] = Field(description="Interview preparation topics.")
