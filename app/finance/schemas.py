from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.finance.models import InvoiceStatus, QuotationStatus


class ItemSchema(BaseModel):
    description: str
    quantity: int
    unit_price: float


class QuotationCreate(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: EmailStr
    items: List[ItemSchema]
    tax_percentage: float = 0.0
    discount_amount: float = 0.0


class QuotationResponse(QuotationCreate):
    id: int
    subtotal: float
    tax_amount: float
    total_amount: float
    status: QuotationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceCreate(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: EmailStr
    items: List[ItemSchema]
    due_date: datetime
    quotation_id: Optional[int] = None


class InvoiceResponse(InvoiceCreate):
    id: int
    total_amount: float
    status: InvoiceStatus
    qr_code_path: Optional[str] = None
    payment_link: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentProcessResponse(BaseModel):
    message: str
    receipt_number: str
    invoice_id: int
    workflow_executed: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)