from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.finance.database import get_db  # Updated import
from app.reporting.schemas import SalesAnalyticsResponse, AIInsightsResponse
from app.reporting.services import (
    generate_sales_analytics,
    generate_ai_forecasting,
)

router = APIRouter()


@router.get("/sales", response_model=SalesAnalyticsResponse)
async def get_sales_analytics(db: Session = Depends(get_db)):
    data = await generate_sales_analytics(db)
    return SalesAnalyticsResponse(**data)


@router.get("/insights", response_model=AIInsightsResponse)
async def get_ai_insights(db: Session = Depends(get_db)):
    sales_data = await generate_sales_analytics(db)
    insights = await generate_ai_forecasting(sales_data)
    return AIInsightsResponse(**insights)