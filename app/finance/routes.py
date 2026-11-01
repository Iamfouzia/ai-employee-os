from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.finance.database import get_db, init_db
from app.finance.schemas import (
    QuotationCreate,
    QuotationResponse,
    InvoiceCreate,
    InvoiceResponse,
    PaymentProcessResponse,
)
from app.finance import crud
from app.finance.pdf_generator import generate_invoice_pdf
from app.finance.models import Invoice

init_db()

router = APIRouter(prefix="/api/finance", tags=["Finance & Accounting"])


@router.post(
    "/quotations",
    response_model=QuotationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation_endpoint(
    data: QuotationCreate, db: Session = Depends(get_db)
):
    return crud.create_quotation(db, data)


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_endpoint(data: InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db, data)


@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Invoice).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    pdf_path = generate_invoice_pdf(invoice)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Invoice_{invoice.id}.pdf",
    )


@router.post(
    "/invoices/{invoice_id}/pay", response_model=PaymentProcessResponse
)
def process_payment_workflow(invoice_id: int, db: Session = Depends(get_db)):
    try:
        return crud.execute_payment_workflow(db, invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))