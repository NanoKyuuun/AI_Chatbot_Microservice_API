from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import json
import uuid
import time

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.document import DocumentUploadResponse, DocumentStatusRead, StandardResponse, ResponseMeta
from app.services.document_service import DocumentService
from app.db.repositories.document_repository import DocumentRepository
from app.core.errors import AppError
from app.core.rate_limit import general_rate_limit, upload_rate_limit

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", 
    response_model=StandardResponse[DocumentUploadResponse],
    dependencies=[Depends(upload_rate_limit)]
)
async def upload_document(
    file: UploadFile = File(...),
    collection_uuid: str = Form(...),
    title: str = Form(...),
    external_document_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None), # JSON string
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Upload a document and start indexing."""
    tenant_id = auth_data["tenant_id"]
    
    # Parse metadata if provided
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Invalid JSON format for metadata",
                status_code=status.HTTP_404_NOT_FOUND
            )

    service = DocumentService(db)
    document, job = await service.upload_document(
        tenant_id=tenant_id,
        collection_uuid=collection_uuid,
        file=file,
        title=title,
        external_document_id=external_document_id,
        metadata=metadata_dict
    )
    
    return StandardResponse(
        data=DocumentUploadResponse(
            document_uuid=document.document_uuid,
            job_uuid=job.job_uuid,
            status=document.status
        ),
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.get("", 
    response_model=StandardResponse[List[DocumentStatusRead]],
    dependencies=[Depends(general_rate_limit)]
)
async def list_documents(
    collection_uuid: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """List all documents for the tenant."""
    tenant_id = auth_data["tenant_id"]
    service = DocumentService(db)
    
    documents = await service.list_documents(
        tenant_id=tenant_id,
        collection_uuid=collection_uuid,
        skip=skip,
        limit=limit
    )
    
    return StandardResponse(
        data=documents,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.get("/{document_uuid}", 
    response_model=StandardResponse[DocumentStatusRead],
    dependencies=[Depends(general_rate_limit)]
)
async def get_document_status(
    document_uuid: str,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Get the status of a document."""
    tenant_id = auth_data["tenant_id"]
    repo = DocumentRepository(db)
    
    document = await repo.get_by_uuid(tenant_id, document_uuid)
    if not document:
        raise AppError(
            code="DOCUMENT_NOT_FOUND",
            message=f"Document {document_uuid} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return StandardResponse(
        data=document,
        meta=ResponseMeta(request_id=str(uuid.uuid4()))
    )

@router.delete("/{document_uuid}", 
    dependencies=[Depends(general_rate_limit)]
)
async def delete_document(
    document_uuid: str,
    db: AsyncSession = Depends(get_db),
    auth_data: dict = Depends(validate_api_key)
):
    """Delete a document and its vectors."""
    tenant_id = auth_data["tenant_id"]
    service = DocumentService(db)
    
    await service.delete_document(tenant_id, document_uuid)
    
    return {
        "success": True,
        "data": {"document_uuid": document_uuid, "status": "deleted"},
        "meta": {"request_id": str(uuid.uuid4()), "timestamp": time.time()}
    }
