from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing Module Imports
from app.communication.api import router as communication_router
from app.communication.whatsapp.api import router as whatsapp_router
from app.crm.routes import router as crm_router
from app.crm.database import init_db as init_crm_db

# AI Brain / Executive Assistant Imports
from app.api.routes import router as assistant_router

# Auth Module Imports (merged from Mariam's standalone backend)
from app.auth.database import init_db as init_auth_db
from app.auth.api import router as auth_router
from app.auth.pricing import router as pricing_router

# Finance Module Imports
from app.finance.database import init_db as init_finance_db
from app.finance.routes import router as finance_router

# Documents & Reporting Imports
from app.documents.api import router as documents_router
from app.reporting.api import router as reporting_router
from app.documents.models import Document  # Explicitly import model to bind metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_crm_db()
    init_finance_db()
    init_auth_db()
    yield


app = FastAPI(
    title="AI Employee OS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "AI Employee OS",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# Router Registrations
app.include_router(auth_router)
app.include_router(pricing_router)
app.include_router(assistant_router)
app.include_router(communication_router)
app.include_router(whatsapp_router)
app.include_router(crm_router)
app.include_router(finance_router)
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(reporting_router, prefix="/api/reports", tags=["Reporting & Analytics"])