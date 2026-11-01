from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db, require_role
from app.auth.models import User, PlanTier, PLAN_LIMITS

router = APIRouter(prefix="/api/pricing", tags=["pricing"])

PLAN_PRICES_USD = {PlanTier.BASIC: 19, PlanTier.PRO: 49, PlanTier.BUSINESS: 149}


@router.get("/plans")
def list_plans():
    return [
        {
            "tier": tier.value,
            "price_usd_per_month": PLAN_PRICES_USD[tier],
            "limits": limits,
        }
        for tier, limits in PLAN_LIMITS.items()
    ]


@router.get("/usage")
def current_usage(current_user: User = Depends(get_current_user)):
    org = current_user.organization
    limits = PLAN_LIMITS[org.plan_tier]
    return {
        "plan_tier": org.plan_tier.value,
        "ai_requests_used": org.ai_requests_used,
        "ai_requests_limit": limits["ai_requests"],
        "seats_used": len(org.users),
        "seats_limit": limits["users"],
    }


def enforce_ai_request_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    org = current_user.organization
    limit = PLAN_LIMITS[org.plan_tier]["ai_requests"]

    if limit is not None and org.ai_requests_used >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"AI request limit reached for the {org.plan_tier.value} plan. Please upgrade.",
        )

    org.ai_requests_used += 1
    db.add(org)
    db.commit()
    return current_user


@router.post("/upgrade")
def upgrade_plan(
    new_tier: PlanTier,
    current_user: User = Depends(require_role("owner", "admin")),
    db: Session = Depends(get_db),
):
    org = current_user.organization
    org.plan_tier = new_tier
    db.add(org)
    db.commit()
    return {"plan_tier": org.plan_tier.value}