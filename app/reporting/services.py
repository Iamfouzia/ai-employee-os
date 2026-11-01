from calendar import month_abbr
from typing import Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.finance.models import Invoice, InvoiceStatus
from app.core.llm_router import route_and_generate


async def generate_sales_analytics(db_session: Session) -> Dict[str, Any]:
    paid_invoices = (
        db_session.query(Invoice)
        .filter(Invoice.status == InvoiceStatus.PAID)
        .all()
    )

    total_orders = len(paid_invoices)
    total_revenue = sum(inv.total_amount for inv in paid_invoices)
    average_order_value = (total_revenue / total_orders) if total_orders else 0.0

    revenue_by_month: Dict[str, float] = {}
    for inv in paid_invoices:
        if inv.created_at is None:
            continue
        label = month_abbr[inv.created_at.month]
        revenue_by_month[label] = revenue_by_month.get(label, 0.0) + inv.total_amount

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "average_order_value": round(average_order_value, 2),
        "revenue_by_month": revenue_by_month,
    }


async def generate_ai_forecasting(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
    if analytics_data["total_orders"] == 0:
        return {
            "insights": ["No paid invoices yet - not enough data to generate insights."],
            "forecast_next_quarter": 0.0,
            "recommendations": ["Start recording paid invoices to unlock AI forecasting."],
        }

    system_prompt = (
        "You are a financial analyst AI. You will be given real sales figures as JSON. "
        "Respond with ONLY a JSON object (no markdown, no commentary) with exactly these keys: "
        '"insights" (array of 2-3 short strings), '
        '"forecast_next_quarter" (a single number), '
        '"recommendations" (array of 2-3 short actionable strings). '
        "Base every insight strictly on the numbers given - do not invent figures."
    )
    user_prompt = f"Sales data: {analytics_data}"

    result = route_and_generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        text_for_complexity=user_prompt,
    )

    import json
    try:
        parsed = json.loads(result["text"])
        return {
            "insights": parsed.get("insights", []),
            "forecast_next_quarter": parsed.get("forecast_next_quarter", 0.0),
            "recommendations": parsed.get("recommendations", []),
        }
    except (json.JSONDecodeError, TypeError):
        return {
            "insights": [result["text"]],
            "forecast_next_quarter": analytics_data["total_revenue"],
            "recommendations": [],
        }