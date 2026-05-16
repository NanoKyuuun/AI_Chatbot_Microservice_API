from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.search import SemanticSearchRequest, SemanticSearchResponse
from app.schemas.document import StandardResponse, ResponseMeta
from app.services.search_service import SearchService
from app.core.rate_limit import general_rate_limit

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", 
    response_model=StandardResponse[SemanticSearchResponse],
    dependencies=[Depends(general_rate_limit)]
)
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """
    Perform semantic search in a collection.
    """
    tenant_id = auth_data["tenant_id"]
    service = SearchService(db)
    
    results = await service.semantic_search(tenant_id, request)
    
    return StandardResponse(
        data=SemanticSearchResponse(results=results),
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )
