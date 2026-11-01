from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from app.crm.database import Base


def utc_now() -> datetime:
    """Return the current UTC time. Used as a default for timestamp columns."""
    return datetime.now(timezone.utc)


class Customer(Base):
    """Represents a business customer/contact tracked in the CRM."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    
    leads = relationship(
        "Lead", back_populates="customer", cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.id} customer_name={self.customer_name!r}>"


class Lead(Base):
    """Represents a sales lead/opportunity tied to a customer."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source = Column(String(100), nullable=True)  
    status = Column(String(50), nullable=False, default="New", index=True)
    
    assigned_to = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    customer = relationship("Customer", back_populates="leads")

    def __repr__(self) -> str:
        return f"<Lead id={self.id} customer_id={self.customer_id} status={self.status!r}>"


class Task(Base):
    """Represents an internal task (not necessarily tied to a customer)."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    assigned_to = Column(String(255), nullable=True, index=True)
    priority = Column(String(20), nullable=False, default="Medium")  
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="Pending", index=True)
    # Expected values: Pending, In-Progress, Done
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status!r}>"


class Activity(Base):
    """Represents a single logged interaction with a customer (the
    'Activity Timeline' feature: calls, emails, meetings, WhatsApp, etc.)."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type = Column(String(50), nullable=False)  
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    customer = relationship("Customer", back_populates="activities")

    def __repr__(self) -> str:
        return f"<Activity id={self.id} customer_id={self.customer_id} type={self.type!r}>"
