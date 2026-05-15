import os
from typing import BinaryIO, Optional
from app.providers.storage import get_storage_provider
from app.db.repositories.document_repository import DocumentRepository
from app.db.repositories.collection_repository import CollectionRepository
from app.schemas.document import DocumentCreate
from app.core.errors import AppError
from fastapi import status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.col_repo = CollectionRepository(db)
        self.storage = get_storage_provider()

    async def upload_document(
        self, 
        tenant_id: str, 
        collection_uuid: str,
        file: UploadFile,
        title: str,
        external_document_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        # 1. Verify collection exists
        collection = await self.col_repo.get_by_uuid(tenant_id, collection_uuid)
        if not collection:
            raise AppError(
                code="COLLECTION_NOT_FOUND",
                message=f"Collection {collection_uuid} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # 2. Prepare file info
        file_ext = os.path.splitext(file.filename)[1].lower().replace(".", "")
        # Relative path for local storage as per PRD: documents/original/{uuid}.{ext}
        import uuid
        file_uuid = str(uuid.uuid4())
        relative_path = f"documents/original/{file_uuid}.{file_ext}"

        # 3. Save file to storage
        try:
            await self.storage.save_file(file.file, relative_path, tenant_id)
        except Exception as e:
            logger.exception("document_storage_failed", tenant_id=tenant_id, error=str(e))
            raise AppError(
                code="STORAGE_ERROR",
                message="Failed to save document to storage",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 4. Create document record
        doc_in = DocumentCreate(
            collection_uuid=collection_uuid,
            title=title,
            external_document_id=external_document_id,
            metadata=metadata
        )
        
        file_info = {
            "file_name": file.filename,
            "file_type": file_ext,
            "mime_type": file.content_type,
            "file_size_bytes": file.size,
            "storage_path": relative_path
        }
        
        document = await self.doc_repo.create(tenant_id, doc_in, file_info)

        # 5. Create indexing job
        job = await self.doc_repo.create_indexing_job(tenant_id, document.document_uuid)

        # 6. Trigger background task (TBD in Issue #16)
        logger.info("indexing_job_created", job_uuid=job.job_uuid, document_uuid=document.document_uuid)
        
        return document, job
