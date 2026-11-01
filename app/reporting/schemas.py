from typing import Dict, List, Any
from pydantic import BaseModel


class SalesAnalyticsResponse(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    revenue_by_month: Dict[str, float]


class AIInsightsResponse(BaseModel):
    insights: List[str]
    forecast_next_quarter: float
    recommendations: List[str]