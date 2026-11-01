import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship

from app.auth.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PlanTier(str, enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    BUSINESS = "business"


PLAN_LIMITS = {
    PlanTier.BASIC: {"users": 1, "ai_requests": 500, "invoices": 100, "quotations": 100, "storage_gb": 1},
    PlanTier.PRO: {"users": 5, "ai_requests": 10_000, "invoices": None, "quotations": None, "storage_gb": 20},
    PlanTier.BUSINESS: {"users": None, "ai_requests": None, "invoices": None, "quotations": None, "storage_gb": 200},
}


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    plan_tier = Column(SQLEnum(PlanTier), default=PlanTier.BASIC, nullable=False)
    ai_requests_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    users = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(64), nullable=True)

    role = Column(String(50), default="member")  # owner, admin, member
    department = Column(String(100), nullable=True)

    organization_id = Column(String(36), ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")

    created_at = Column(DateTime(timezone=True), default=utc_now)