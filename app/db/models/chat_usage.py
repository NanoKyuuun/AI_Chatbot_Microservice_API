from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, BigInteger, TIMESTAMP, Enum, func, JSON, Text, Integer, Text, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum

class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class UsageStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    external_user_id: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    collection_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    session_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    retrieval_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    filters: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    retrieved_chunks: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    top_k: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usage_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    client_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    api_key_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 6), nullable=True)
    status: Mapped[UsageStatus] = mapped_column(Enum(UsageStatus), nullable=False, default=UsageStatus.SUCCESS)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), index=True
    )

class ModelConfig(Base):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    config_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(150), nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0.20)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    top_p: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

class AnswerFeedback(Base):
    __tablename__ = "answer_feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    feedback_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    message_uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
