from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.usage_repository import UsageRepository
from app.db.models.chat_usage import UsageStatus
from datetime import datetime
from app.core.logging import logger

class UsageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UsageRepository(db)

    async def log_chat_usage(
        self,
        tenant_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        client_uuid: Optional[str] = None,
        api_key_uuid: Optional[str] = None
    ):
        """Log chat completion usage."""
        # Simple cost estimation (e.g., $0.01 per 1k tokens as a placeholder)
        estimated_cost = (total_tokens / 1000) * 0.01
        
        await self.repo.create_log(
            tenant_id=tenant_id,
            endpoint="/v1/chat",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            client_uuid=client_uuid,
            api_key_uuid=api_key_uuid
        )
        logger.info("usage_logged", tenant_id=tenant_id, tokens=total_tokens)

    async def log_search_usage(
        self,
        tenant_id: str,
        embedding_model: str,
        tokens: int,
        client_uuid: Optional[str] = None,
        api_key_uuid: Optional[str] = None
    ):
        """Log semantic search usage (embeddings)."""
        # Simple cost estimation for embeddings
        estimated_cost = (tokens / 1000) * 0.001
        
        await self.repo.create_log(
            tenant_id=tenant_id,
            endpoint="/v1/search",
            embedding_model=embedding_model,
            prompt_tokens=tokens,
            total_tokens=tokens,
            estimated_cost=estimated_cost,
            client_uuid=client_uuid,
            api_key_uuid=api_key_uuid
        )

    async def log_error(
        self,
        tenant_id: str,
        endpoint: str,
        error_code: str,
        client_uuid: Optional[str] = None,
        api_key_uuid: Optional[str] = None
    ):
        """Log a failed request."""
        await self.repo.create_log(
            tenant_id=tenant_id,
            endpoint=endpoint,
            status=UsageStatus.FAILED,
            error_code=error_code,
            client_uuid=client_uuid,
            api_key_uuid=api_key_uuid
        )

    async def get_usage_summary(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get summarized usage reports."""
        summary = await self.repo.get_summary(tenant_id, start_date, end_date)
        by_model = await self.repo.get_summary_by_model(tenant_id, start_date, end_date)
        
        summary["by_model"] = by_model
        return summary
