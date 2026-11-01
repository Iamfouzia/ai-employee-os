import os
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PDF_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "generated_pdfs"
)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


def generate_qr_code(invoice_id: int, amount: float) -> str:
    qr_data = f"PAY-INVOICE-{invoice_id}-AMOUNT-{amount}"
    qr = qrcode.make(qr_data)
    qr_path = os.path.join(PDF_OUTPUT_DIR, f"qr_invoice_{invoice_id}.png")
    qr.save(qr_path)
    return qr_path


def generate_invoice_pdf(invoice) -> str:
    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"invoice_{invoice.id}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "AI EMPLOYEE OS - INVOICE")

    c.setFont("Helvetica", 10)
    c.drawString(100, 730, f"Invoice ID: #{invoice.id}")
    c.drawString(100, 715, f"Customer: {invoice.customer_name}")
    c.drawString(100, 700, f"Email: {invoice.customer_email}")

    y = 660
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y, "Item Description")
    c.drawString(300, y, "Qty")
    c.drawString(400, y, "Price")

    c.setFont("Helvetica", 10)
    for item in invoice.items:
        y -= 20
        c.drawString(100, y, item["description"])
        c.drawString(300, y, str(item["quantity"]))
        c.drawString(400, y, f"${item['unit_price']:.2f}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, f"Total Amount Due: ${invoice.total_amount:.2f}")

    if invoice.qr_code_path and os.path.exists(invoice.qr_code_path):
        c.drawImage(invoice.qr_code_path, 400, y - 100, width=100, height=100)

    c.save()
    return pdf_path