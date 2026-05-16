from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.chat_repository import ChatRepository
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.core.errors import AppError
from fastapi import status
from app.db.models.chat_usage import ChatMessage

class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FeedbackRepository(db)
        self.chat_repo = ChatRepository(db)

    async def create_feedback(
        self, 
        tenant_id: str, 
        obj_in: FeedbackCreate
    ) -> FeedbackRead:
        # 1. Verify message exists and belongs to tenant
        query = select(ChatMessage).where(
            ChatMessage.tenant_uuid == tenant_id,
            ChatMessage.message_uuid == obj_in.message_uuid
        )
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise AppError(
                code="MESSAGE_NOT_FOUND",
                message=f"Message {obj_in.message_uuid} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # 2. Create feedback
        feedback = await self.repo.create(
            tenant_id=tenant_id,
            obj_in=obj_in,
            session_uuid=message.session_uuid
        )
        
        return feedback
