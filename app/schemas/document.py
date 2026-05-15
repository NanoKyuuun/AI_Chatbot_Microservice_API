from datetime import datetime
from typing import Optional, Any, List
from pydantic import Field
from app.schemas.collection import BaseSchema, StandardResponse, ResponseMeta

class DocumentBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    external_document_id: Optional[str] = Field(None, max_length=150)
    metadata_: Optional[dict[str, Any]] = Field(None, alias="metadata")

class DocumentCreate(DocumentBase):
    collection_uuid: str
    indexing_mode: str = "async" # sync or async

class DocumentRead(DocumentBase):
    document_uuid: str
    tenant_uuid: str
    collection_uuid: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    status: str
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class DocumentStatusRead(BaseSchema):
    document_uuid: str
    title: str
    status: str
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    created_at: datetime

class DocumentUploadResponse(BaseSchema):
    document_uuid: str
    job_uuid: Optional[str] = None
    status: str
