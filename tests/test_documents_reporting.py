import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.finance.database import init_db as init_finance_db
from app.crm.database import init_db as init_crm_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database tables are created before running tests."""
    init_crm_db()
    init_finance_db()


@pytest.fixture
def client():
    """Provide TestClient with lifespan context initialized."""
    with TestClient(app) as test_client:
        yield test_client


def test_upload_document(client):
    files = {"file": ("test_policy.pdf", b"Company Remote Work Policy text content", "application/pdf")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["filename"] == "test_policy.pdf"
    assert "extracted_text" in data


def test_document_ai_qa(client):
    payload = {"query": "What is the remote work policy?"}
    response = client.post("/api/documents/qa", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()


def test_sales_analytics(client):
    response = client.get("/api/reports/sales")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "revenue_by_month" in data


def test_ai_insights(client):
    response = client.get("/api/reports/insights")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "forecast_next_quarter" in data