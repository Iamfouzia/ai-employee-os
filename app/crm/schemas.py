from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Customer schemas

class CustomerBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)


class CustomerCreate(CustomerBase):
    """Payload required to create a new customer."""
    pass


class CustomerUpdate(BaseModel):
    """Payload for partially updating a customer. All fields optional."""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

# Lead schemas

LeadStatus = Literal["New", "Contacted", "Negotiation", "Closed"]


class LeadBase(BaseModel):
    customer_id: int
    source: Optional[str] = Field(None, max_length=100)
    status: LeadStatus = "New"
    assigned_to: Optional[str] = Field(None, max_length=255)


class LeadCreate(LeadBase):
    """Payload required to create a new lead."""
    pass


class LeadUpdate(BaseModel):
    """Payload for partially updating a lead. All fields optional."""
    source: Optional[str] = Field(None, max_length=100)
    status: Optional[LeadStatus] = None
    assigned_to: Optional[str] = Field(None, max_length=255)


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

# Task schemas
TaskPriority = Literal["High", "Medium", "Low"]
TaskStatus = Literal["Pending", "In-Progress", "Done"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    assigned_to: Optional[str] = Field(None, max_length=255)
    priority: TaskPriority = "Medium"
    deadline: Optional[datetime] = None
    status: TaskStatus = "Pending"


class TaskCreate(TaskBase):
    """Payload required to create a new task."""
    pass


class TaskUpdate(BaseModel):
    """Payload for partially updating a task. All fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    assigned_to: Optional[str] = Field(None, max_length=255)
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

# Activity schemas
class ActivityBase(BaseModel):
    customer_id: int
    type: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)


class ActivityCreate(ActivityBase):
    """Payload required to log a new activity for a customer."""
    pass


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime