"""
Structured output schemas for the Executive Assistant's NLU layer.
Every user command gets classified + parsed into one of these shapes.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class IntentCategory(str, Enum):
    """One value per AI Employee (matches the 12 employees in the project PDF),
    plus GENERAL as a catch-all when nothing matches."""
    CEO = "ceo"
    SALES = "sales"
    SUPPORT = "support"
    HR = "hr"
    RECRUITMENT = "recruitment"
    FINANCE = "finance"
    ACCOUNTING = "accounting"
    MARKETING = "marketing"
    CONTENT = "content"
    LEGAL = "legal"
    INVENTORY = "inventory"
    PROCUREMENT = "procurement"
    GENERAL = "general"


class ParsedIntent(BaseModel):
    """Final structured output the Executive Assistant hands off to an AI Employee."""
    category: IntentCategory = Field(..., description="Which AI Employee should handle this")
    action: str = Field(..., description="The action to perform, e.g. 'schedule_meeting', 'send_quotation'")
    customer_name: Optional[str] = Field(None, description="Customer/person mentioned, if any")
    date: Optional[str] = Field(None, description="Date mentioned, in natural or ISO form")
    time: Optional[str] = Field(None, description="Time mentioned, if any")
    quantity: Optional[int] = Field(None, description="Any quantity mentioned, e.g. number of laptops")
    raw_input: str = Field(..., description="Original user command, kept for logging/debugging")
    confidence: float = Field(..., description="Zero-shot classifier confidence score for the category")


class TaskStep(BaseModel):
    """A single sub-task extracted from a multi-step command."""
    step_id: int = Field(..., description="Order of this step, starting at 1")
    category: IntentCategory = Field(..., description="Which AI Employee should handle this step")
    action: str = Field(..., description="Action to perform, e.g. 'send_quotation', 'schedule_meeting'")
    customer_name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    quantity: Optional[int] = None
    depends_on: Optional[int] = Field(None, description="step_id this step waits on, if any (e.g. a reminder waiting on a reply)")
    condition: Optional[str] = Field(None, description="Natural-language condition for conditional steps, e.g. 'if he doesn't reply in 3 days'")
    question_text: Optional[str] = Field(None, description="For 'answer_question' steps - the actual question to look up in the knowledge base")


class TaskPlan(BaseModel):
    """Full multi-step plan the Executive Assistant builds from one raw command."""
    raw_input: str
    steps: list[TaskStep]