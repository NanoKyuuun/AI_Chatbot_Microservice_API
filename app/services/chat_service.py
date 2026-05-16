import time
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.search_service import SearchService
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService
from app.db.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatRequest, ChatResponse, ChatUsage
from app.schemas.search import SemanticSearchRequest
from app.db.models.chat_usage import ChatRole
from app.core.errors import AppError
from fastapi import status
from app.core.logging import logger

from app.services.usage_service import UsageService

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.search_service = SearchService(db)
        self.prompt_service = PromptService()
        self.llm_service = LLMService()
        self.chat_repo = ChatRepository(db)
        self.usage_service = UsageService(db)

    async def chat(self, tenant_id: str, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        # 1. Handle session
        session_uuid = request.session_uuid
        if not session_uuid:
            session = await self.chat_repo.create_session(
                tenant_id=tenant_id,
                external_user_id=request.external_user_id,
                collection_uuid=request.collection_uuid,
                title=request.message[:50] # Simple title
            )
            session_uuid = session.session_uuid
        else:
            session = await self.chat_repo.get_session(tenant_id, session_uuid)
            if not session:
                raise AppError(
                    code="SESSION_NOT_FOUND",
                    message=f"Session {session_uuid} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        # 2. Retrieve context (Search)
        search_request = SemanticSearchRequest(
            collection_uuid=request.collection_uuid,
            query=request.message,
            top_k=request.options.top_k,
            filters=request.filters,
            allowed_document_ids=request.allowed_document_ids,
            include_content=True
        )
        search_results = await self.search_service.semantic_search(tenant_id, search_request)

        # 3. Assemble prompt
        context_str = self.prompt_service.format_context(search_results)
        
        # Optionally load chat history (e.g., last 5 messages)
        # For now, let's keep it simple without history to avoid token blowup
        # But we'll need it for version 1.
        messages = self.prompt_service.build_messages(
            user_query=request.message,
            context_str=context_str
        )

        # 4. Call LLM
        llm_response = await self.llm_service.generate_response(
            messages=messages,
            model=request.options.model,
            temperature=request.options.temperature,
            max_tokens=request.options.max_tokens
        )

        # Log chat usage
        await self.usage_service.log_chat_usage(
            tenant_id=tenant_id,
            model=llm_response["model"],
            prompt_tokens=llm_response["usage"]["prompt_tokens"],
            completion_tokens=llm_response["usage"]["completion_tokens"],
            total_tokens=llm_response["usage"]["total_tokens"]
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # 5. Save messages to DB
        # User message
        await self.chat_repo.save_message(
            tenant_id=tenant_id,
            session_uuid=session_uuid,
            role=ChatRole.USER,
            content=request.message
        )
        
        # Assistant message
        sources_data = [res.dict() for res in search_results] if request.options.with_sources else None
        
        assistant_msg = await self.chat_repo.save_message(
            tenant_id=tenant_id,
            session_uuid=session_uuid,
            role=ChatRole.ASSISTANT,
            content=llm_response["answer"],
            sources={"results": sources_data} if sources_data else None,
            model=llm_response["model"],
            prompt_tokens=llm_response["usage"]["prompt_tokens"],
            completion_tokens=llm_response["usage"]["completion_tokens"],
            total_tokens=llm_response["usage"]["total_tokens"],
            latency_ms=latency_ms
        )

        # 6. Format Response
        return ChatResponse(
            session_uuid=session_uuid,
            message_uuid=assistant_msg.message_uuid,
            answer=llm_response["answer"],
            sources=search_results if request.options.with_sources else None,
            usage=ChatUsage(
                model=llm_response["model"],
                prompt_tokens=llm_response["usage"]["prompt_tokens"],
                completion_tokens=llm_response["usage"]["completion_tokens"],
                total_tokens=llm_response["usage"]["total_tokens"]
            )
        )
