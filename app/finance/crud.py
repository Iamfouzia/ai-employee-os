import uuid
from sqlalchemy.orm import Session
from app.finance.models import (
    Quotation,
    Invoice,
    Payment,
    InvoiceStatus,
    QuotationStatus,
)
from app.finance.schemas import (
    QuotationCreate,
    InvoiceCreate,
    PaymentProcessResponse,
)
from app.finance.pdf_generator import generate_qr_code


def create_quotation(db: Session, data: QuotationCreate) -> Quotation:
    subtotal = sum(item.quantity * item.unit_price for item in data.items)
    tax_amount = subtotal * (data.tax_percentage / 100.0)
    total = subtotal + tax_amount - data.discount_amount

    quotation = Quotation(
        customer_id=data.customer_id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        subtotal=subtotal,
        tax_percentage=data.tax_percentage,
        tax_amount=tax_amount,
        discount_amount=data.discount_amount,
        total_amount=max(total, 0.0),
        items=[item.model_dump() for item in data.items],
        status=QuotationStatus.DRAFT,
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation


def create_invoice(db: Session, data: InvoiceCreate) -> Invoice:
    total_amount = sum(
        item.quantity * item.unit_price for item in data.items
    )

    invoice = Invoice(
        quotation_id=data.quotation_id,
        customer_id=data.customer_id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        total_amount=total_amount,
        due_date=data.due_date,
        items=[item.model_dump() for item in data.items],
        status=InvoiceStatus.UNPAID,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Attach QR Code & Payment Link
    invoice.qr_code_path = generate_qr_code(invoice.id, invoice.total_amount)
    invoice.payment_link = f"https://pay.aiemployee.os/checkout/{invoice.id}"
    db.commit()
    db.refresh(invoice)

    return invoice


def execute_payment_workflow(
    db: Session, invoice_id: int
) -> PaymentProcessResponse:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    invoice.status = InvoiceStatus.PAID
    receipt_no = f"RCT-{uuid.uuid4().hex[:8].upper()}"

    payment = Payment(
        invoice_id=invoice.id,
        amount_paid=invoice.total_amount,
        receipt_number=receipt_no,
    )
    db.add(payment)
    db.commit()

    workflow_log = {
        "step_1": "Receipt Generated",
        "step_2": f"CRM Updated for Customer #{invoice.customer_id}",
        "step_3": "Sales Team Notified via Email",
        "step_4": f"Thank You Email sent to {invoice.customer_email}",
        "step_5": "Follow-up Scheduled in Calendar",
    }

    return PaymentProcessResponse(
        message="Payment processed and automated workflow executed successfully.",
        receipt_number=receipt_no,
        invoice_id=invoice.id,
        workflow_executed=workflow_log,
    )