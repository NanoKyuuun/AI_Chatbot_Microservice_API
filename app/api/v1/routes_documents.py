from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import uuid

from app.db.session import get_db
from app.api.deps import validate_api_key
from app.schemas.document import DocumentUploadResponse, DocumentStatusRead, StandardResponse, ResponseMeta
from app.services.document_service import DocumentService
from app.db.repositories.document_repository import DocumentRepository
from app.core.errors import AppError

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=StandardResponse[DocumentUploadResponse])
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
                status_code=status.HTTP_400_BAD_REQUEST
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

@router.get("/{document_uuid}", response_model=StandardResponse[DocumentStatusRead])
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
