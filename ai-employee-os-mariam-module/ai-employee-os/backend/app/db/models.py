import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class PlanTier(str, enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    BUSINESS = "business"


# AI request quotas per plan tier, enforced by app.api.pricing
PLAN_LIMITS = {
    PlanTier.BASIC: {"users": 1, "ai_requests": 500, "invoices": 100, "quotations": 100, "storage_gb": 1},
    PlanTier.PRO: {"users": 5, "ai_requests": 10_000, "invoices": None, "quotations": None, "storage_gb": 20},
    PlanTier.BUSINESS: {"users": None, "ai_requests": None, "invoices": None, "quotations": None, "storage_gb": 200},
}


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_tier: Mapped[PlanTier] = mapped_column(Enum(PlanTier), default=PlanTier.BASIC)
    ai_requests_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str] = mapped_column(String(64), nullable=True)

    # Department-based permissions (Business plan feature)
    role: Mapped[str] = mapped_column(String(50), default="member")  # owner, admin, member
    department: Mapped[str] = mapped_column(String(100), nullable=True)

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    organization: Mapped["Organization"] = relationship(back_populates="users")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
