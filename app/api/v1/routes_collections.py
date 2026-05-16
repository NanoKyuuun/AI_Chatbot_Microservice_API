from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import time

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.collection import CollectionCreate, CollectionUpdate, CollectionRead, StandardResponse, ResponseMeta
from app.db.repositories.collection_repository import CollectionRepository
from app.core.errors import AppError
from app.core.rate_limit import general_rate_limit

router = APIRouter(prefix="/collections", tags=["collections"])

@router.post("", 
    response_model=StandardResponse[CollectionRead],
    dependencies=[Depends(general_rate_limit)]
)
async def create_collection(
    obj_in: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Create a new collection for the tenant."""
    repo = CollectionRepository(db)
    tenant_id = auth_data["tenant_id"]
    
    collection = await repo.create(tenant_id, obj_in)
    
    return StandardResponse(
        data=collection,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.get("", 
    response_model=StandardResponse[List[CollectionRead]],
    dependencies=[Depends(general_rate_limit)]
)
async def list_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """List all collections for the tenant."""
    repo = CollectionRepository(db)
    tenant_id = auth_data["tenant_id"]
    
    collections = await repo.get_multi(tenant_id, skip=skip, limit=limit)
    
    return StandardResponse(
        data=collections,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.get("/{collection_uuid}", 
    response_model=StandardResponse[CollectionRead],
    dependencies=[Depends(general_rate_limit)]
)
async def get_collection(
    collection_uuid: str,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Get a specific collection by UUID."""
    repo = CollectionRepository(db)
    tenant_id = auth_data["tenant_id"]
    
    collection = await repo.get_by_uuid(tenant_id, collection_uuid)
    if not collection:
        raise AppError(
            code="COLLECTION_NOT_FOUND",
            message=f"Collection with UUID {collection_uuid} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return StandardResponse(
        data=collection,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.patch("/{collection_uuid}", 
    response_model=StandardResponse[CollectionRead],
    dependencies=[Depends(general_rate_limit)]
)
async def update_collection(
    collection_uuid: str,
    obj_in: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Update a collection."""
    repo = CollectionRepository(db)
    tenant_id = auth_data["tenant_id"]
    
    collection = await repo.get_by_uuid(tenant_id, collection_uuid)
    if not collection:
        raise AppError(
            code="COLLECTION_NOT_FOUND",
            message=f"Collection with UUID {collection_uuid} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    updated_collection = await repo.update(collection, obj_in)
    
    return StandardResponse(
        data=updated_collection,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.delete("/{collection_uuid}", 
    dependencies=[Depends(general_rate_limit)]
)
async def delete_collection(
    collection_uuid: str,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Delete a collection."""
    repo = CollectionRepository(db)
    tenant_id = auth_data["tenant_id"]
    
    collection = await repo.get_by_uuid(tenant_id, collection_uuid)
    if not collection:
        raise AppError(
            code="COLLECTION_NOT_FOUND",
            message=f"Collection with UUID {collection_uuid} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    await repo.delete(collection)
    
    return {
        "success": True,
        "data": {"document_uuid": collection_uuid, "status": "deleted"},
        "meta": {"request_id": str(uuid.uuid4()), "timestamp": time.time()}
    }
