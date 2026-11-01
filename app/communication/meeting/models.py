from pydantic import BaseModel, Field


class MeetingTranscript(BaseModel):
    title: str
    transcript: str


class MeetingAnalysis(BaseModel):
    summary: str
    speakers: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)