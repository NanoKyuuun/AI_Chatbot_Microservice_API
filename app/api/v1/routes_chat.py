from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import StandardResponse, ResponseMeta
from app.services.chat_service import ChatService
from app.core.rate_limit import chat_rate_limit

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", 
    response_model=StandardResponse[ChatResponse],
    dependencies=[Depends(chat_rate_limit)]
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """
    Chat with the AI using documents in a collection (RAG).
    """
    tenant_id = auth_data["tenant_id"]
    service = ChatService(db)
    
    result = await service.chat(tenant_id, request)
    
    return StandardResponse(
        data=result,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )
