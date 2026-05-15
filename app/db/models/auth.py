from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, BigInt, TIMESTAMP, Enum, func, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum

class APIClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class APIKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"

class APIClient(Base):
    __tablename__ = "api_clients"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    client_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[APIClientStatus] = mapped_column(
        Enum(APIClientStatus), nullable=False, default=APIClientStatus.ACTIVE
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    key_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    client_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    scopes: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[APIKeyStatus] = mapped_column(
        Enum(APIKeyStatus), nullable=False, default=APIKeyStatus.ACTIVE
    )
    
    last_used_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
