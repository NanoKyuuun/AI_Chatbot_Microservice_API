import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document import Document, DocumentStatus, IndexingJob, JobStatus
from app.schemas.document import DocumentCreate

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant_id: str, obj_in: DocumentCreate, file_info: dict = None) -> Document:
        document_uuid = str(uuid.uuid4())
        
        db_obj = Document(
            document_uuid=document_uuid,
            tenant_uuid=tenant_id,
            collection_uuid=obj_in.collection_uuid,
            external_document_id=obj_in.external_document_id,
            title=obj_in.title,
            metadata_=obj_in.metadata_,
            status=DocumentStatus.UPLOADED
        )
        
        if file_info:
            db_obj.file_name = file_info.get("file_name")
            db_obj.file_type = file_info.get("file_type")
            db_obj.mime_type = file_info.get("mime_type")
            db_obj.file_size_bytes = file_info.get("file_size_bytes")
            db_obj.storage_path = file_info.get("storage_path")

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_uuid(self, tenant_id: str, document_uuid: str) -> Optional[Document]:
        query = select(Document).where(
            Document.tenant_uuid == tenant_id,
            Document.document_uuid == document_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_indexing_job(self, tenant_id: str, document_uuid: str) -> IndexingJob:
        job_uuid = str(uuid.uuid4())
        db_obj = IndexingJob(
            job_uuid=job_uuid,
            tenant_uuid=tenant_id,
            document_uuid=document_uuid,
            status=JobStatus.QUEUED,
            progress=0
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_job_by_uuid(self, tenant_id: str, job_uuid: str) -> Optional[IndexingJob]:
        query = select(IndexingJob).where(
            IndexingJob.tenant_uuid == tenant_id,
            IndexingJob.job_uuid == job_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
