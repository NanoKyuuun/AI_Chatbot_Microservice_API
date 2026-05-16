from datetime import datetime
from typing import Optional
from sqlalchemy import String, BigInteger, TIMESTAMP, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), nullable=False, default=TenantStatus.ACTIVE
    )
    default_model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    default_embedding_model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    monthly_quota_tokens: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    monthly_quota_requests: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
