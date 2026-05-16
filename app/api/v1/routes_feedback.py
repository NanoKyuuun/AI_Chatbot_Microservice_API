from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.schemas.document import StandardResponse, ResponseMeta
from app.services.feedback_service import FeedbackService
from app.core.rate_limit import general_rate_limit

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("", 
    response_model=StandardResponse[FeedbackRead],
    dependencies=[Depends(general_rate_limit)]
)
async def create_feedback(
    obj_in: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """
    Submit feedback for an AI response.
    """
    tenant_id = auth_data["tenant_id"]
    service = FeedbackService(db)
    
    feedback = await service.create_feedback(tenant_id, obj_in)
    
    return StandardResponse(
        data=feedback,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )
