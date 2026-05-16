from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.document import StandardResponse, ResponseMeta
from app.services.usage_service import UsageService
from app.core.rate_limit import general_rate_limit

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("", 
    response_model=StandardResponse[Dict[str, Any]],
    dependencies=[Depends(general_rate_limit)]
)
async def get_usage_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """
    Get summary of AI usage for the tenant.
    """
    tenant_id = auth_data["tenant_id"]
    service = UsageService(db)
    
    # Default to last 30 days if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
        
    summary = await service.get_usage_summary(tenant_id, start_date, end_date)
    
    return StandardResponse(
        data=summary,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )
