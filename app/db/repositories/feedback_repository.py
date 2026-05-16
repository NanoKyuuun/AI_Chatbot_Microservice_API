import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat_usage import AnswerFeedback
from app.schemas.feedback import FeedbackCreate

class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, 
        tenant_id: str, 
        obj_in: FeedbackCreate,
        session_uuid: Optional[str] = None
    ) -> AnswerFeedback:
        feedback_uuid = str(uuid.uuid4())
        db_obj = AnswerFeedback(
            feedback_uuid=feedback_uuid,
            tenant_uuid=tenant_id,
            session_uuid=session_uuid,
            message_uuid=obj_in.message_uuid,
            rating=obj_in.rating,
            is_helpful=obj_in.is_helpful,
            reason=obj_in.reason,
            metadata_=obj_in.metadata
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_uuid(self, tenant_id: str, feedback_uuid: str) -> Optional[AnswerFeedback]:
        query = select(AnswerFeedback).where(
            AnswerFeedback.tenant_uuid == tenant_id,
            AnswerFeedback.feedback_uuid == feedback_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
