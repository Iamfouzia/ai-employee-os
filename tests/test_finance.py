import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.main import app

client = TestClient(app)


def test_create_quotation():
    payload = {
        "customer_id": 1,
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "items": [
            {"description": "Laptop", "quantity": 2, "unit_price": 1000.0}
        ],
        "tax_percentage": 10.0,
        "discount_amount": 100.0,
    }
    response = client.post("/api/finance/quotations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 2000.0
    assert data["tax_amount"] == 200.0
    assert data["total_amount"] == 2100.0


def test_invoice_and_payment_workflow():
    due = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    invoice_payload = {
        "customer_id": 1,
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "due_date": due,
        "items": [
            {"description": "Consulting", "quantity": 5, "unit_price": 100.0}
        ],
    }
    inv_resp = client.post("/api/finance/invoices", json=invoice_payload)
    assert inv_resp.status_code == 201
    inv_id = inv_resp.json()["id"]

    # Process Payment
    pay_resp = client.post(f"/api/finance/invoices/{inv_id}/pay")
    assert pay_resp.status_code == 200
    assert "RCT-" in pay_resp.json()["receipt_number"]
    assert (
        pay_resp.json()["workflow_executed"]["step_1"] == "Receipt Generated"
    )