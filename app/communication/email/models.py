from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailCategory(str, Enum):
    GENERAL = "general"
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"
    MEETING = "meeting"
    HR = "hr"
    SPAM = "spam"


class EmailMessage(BaseModel):
    message_id: str | None = None
    thread_id: str | None = None

    sender: str
    recipients: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)

    subject: str = ""
    body: str

    received_at: datetime | None = None


class EmailAnalysis(BaseModel):
    summary: str

    category: EmailCategory = EmailCategory.GENERAL
    priority: EmailPriority = EmailPriority.NORMAL

    requires_reply: bool = False
    suggested_follow_up_at: datetime | None = None


class EmailDraftRequest(BaseModel):
    recipients: list[str]

    subject: str = ""
    context: str

    tone: str = "professional"


class EmailDraftResponse(BaseModel):
    subject: str
    body: str