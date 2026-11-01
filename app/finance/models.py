import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from app.finance.database import Base


class QuotationStatus(str, enum.Enum):
    DRAFT = "Draft"
    PENDING = "Pending Approval"
    APPROVED = "Approved"
    SENT = "Sent"
    REJECTED = "Rejected"


class InvoiceStatus(str, enum.Enum):
    UNPAID = "Unpaid"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    subtotal = Column(Float, default=0.0)
    tax_percentage = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(
        SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT, nullable=False
    )
    items = Column(JSON, nullable=False, default=list)  # List of dicts
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invoices = relationship("Invoice", back_populates="quotation")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(
        Integer, ForeignKey("quotations.id"), nullable=True
    )
    customer_id = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(
        SQLEnum(InvoiceStatus), default=InvoiceStatus.UNPAID, nullable=False
    )
    qr_code_path = Column(String, nullable=True)
    payment_link = Column(String, nullable=True)
    items = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    quotation = relationship("Quotation", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(
        Integer, ForeignKey("invoices.id"), nullable=False
    )
    amount_paid = Column(Float, nullable=False)
    receipt_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="payments")