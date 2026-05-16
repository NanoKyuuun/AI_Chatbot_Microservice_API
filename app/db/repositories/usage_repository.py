import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat_usage import UsageLog, UsageStatus
from datetime import datetime

class UsageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        tenant_id: str,
        endpoint: str,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        estimated_cost: float = 0.0,
        client_uuid: Optional[str] = None,
        api_key_uuid: Optional[str] = None,
        status: UsageStatus = UsageStatus.SUCCESS,
        error_code: Optional[str] = None
    ) -> UsageLog:
        usage_uuid = str(uuid.uuid4())
        db_obj = UsageLog(
            usage_uuid=usage_uuid,
            tenant_uuid=tenant_id,
            client_uuid=client_uuid,
            api_key_uuid=api_key_uuid,
            endpoint=endpoint,
            model=model,
            embedding_model=embedding_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            status=status,
            error_code=error_code
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_summary(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get aggregated usage summary for a tenant in a date range.
        """
        query = select(
            func.count(UsageLog.id).label("total_requests"),
            func.sum(UsageLog.total_tokens).label("total_tokens"),
            func.sum(UsageLog.estimated_cost).label("total_cost")
        ).where(
            and_(
                UsageLog.tenant_uuid == tenant_id,
                UsageLog.created_at >= start_date,
                UsageLog.created_at <= end_date
            )
        )
        
        result = await self.db.execute(query)
        row = result.fetchone()
        
        return {
            "total_requests": row.total_requests or 0,
            "total_tokens": int(row.total_tokens or 0),
            "estimated_cost": float(row.total_cost or 0.0)
        }

    async def get_summary_by_model(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get usage summary grouped by model.
        """
        query = select(
            UsageLog.model,
            func.count(UsageLog.id).label("requests"),
            func.sum(UsageLog.total_tokens).label("tokens")
        ).where(
            and_(
                UsageLog.tenant_uuid == tenant_id,
                UsageLog.created_at >= start_date,
                UsageLog.created_at <= end_date,
                UsageLog.model.isnot(None)
            )
        ).group_by(UsageLog.model)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "model": row.model,
                "requests": row.requests,
                "tokens": int(row.tokens or 0)
            } for row in rows
        ]
