import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat_usage import ChatSession, ChatMessage, ChatRole
from datetime import datetime

class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, 
        tenant_id: str, 
        external_user_id: Optional[str] = None,
        collection_uuid: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        session_uuid = str(uuid.uuid4())
        db_obj = ChatSession(
            session_uuid=session_uuid,
            tenant_uuid=tenant_id,
            external_user_id=external_user_id,
            collection_uuid=collection_uuid,
            title=title,
            metadata_=metadata
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_session(self, tenant_id: str, session_uuid: str) -> Optional[ChatSession]:
        query = select(ChatSession).where(
            ChatSession.tenant_uuid == tenant_id,
            ChatSession.session_uuid == session_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def save_message(
        self,
        tenant_id: str,
        session_uuid: str,
        role: ChatRole,
        content: str,
        sources: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None
    ) -> ChatMessage:
        message_uuid = str(uuid.uuid4())
        db_obj = ChatMessage(
            message_uuid=message_uuid,
            session_uuid=session_uuid,
            tenant_uuid=tenant_id,
            role=role,
            content=content,
            sources=sources,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_messages(
        self, 
        tenant_id: str, 
        session_uuid: str, 
        limit: int = 50
    ) -> List[ChatMessage]:
        query = select(ChatMessage).where(
            ChatMessage.tenant_uuid == tenant_id,
            ChatMessage.session_uuid == session_uuid
        ).order_by(ChatMessage.created_at.asc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
