from pydantic import Field
from typing import Optional, Any, Dict
from app.schemas.collection import BaseSchema
from datetime import datetime

class FeedbackCreate(BaseSchema):
    message_uuid: str = Field(..., description="UUID of the chat message being rated")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    is_helpful: Optional[bool] = Field(None, description="Whether the response was helpful")
    reason: Optional[str] = Field(None, description="Qualitative feedback or reason for rating")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for feedback")

class FeedbackRead(FeedbackCreate):
    feedback_uuid: str
    tenant_uuid: str
    session_uuid: Optional[str] = None
    created_at: datetime
