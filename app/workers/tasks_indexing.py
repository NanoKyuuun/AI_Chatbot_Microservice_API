from app.workers.celery_app import celery_app
from app.core.logging import logger
from app.db.session import SessionLocal
from app.db.repositories.document_repository import DocumentRepository
from app.db.repositories.collection_repository import CollectionRepository
from app.db.models.document import DocumentStatus, JobStatus
from app.services.parser_service import ParserService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.providers.storage import get_storage_provider
from app.core.config import settings
import asyncio
import os
import uuid

def run_async(coro):
    """Helper to run async coroutine in sync context."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.create_task(coro)
    return loop.run_until_complete(coro)

@celery_app.task(name="process_document_task")
def process_document_task(tenant_id: str, document_uuid: str, job_uuid: str):
    """
    Complete Background Pipeline to process a document.
    """
    logger.info("process_document_task_started", tenant_id=tenant_id, document_uuid=document_uuid, job_uuid=job_uuid)
    
    return run_async(_process_document(tenant_id, document_uuid, job_uuid))

async def _process_document(tenant_id: str, document_uuid: str, job_uuid: str):
    async with SessionLocal() as db:
        doc_repo = DocumentRepository(db)
        col_repo = CollectionRepository(db)
        storage = get_storage_provider()
        
        # 1. Fetch job and document
        job = await doc_repo.get_job_by_uuid(tenant_id, job_uuid)
        document = await doc_repo.get_by_uuid(tenant_id, document_uuid)
        
        if not job or not document:
            logger.error("indexing_task_not_found", job_uuid=job_uuid, doc_uuid=document_uuid)
            return False

        try:
            # 2. Update job status to 'running'
            await doc_repo.update_job_status(job, JobStatus.RUNNING, progress=10)
            await doc_repo.update_document_status(document, DocumentStatus.PROCESSING)

            # 3. Get file from storage
            full_local_path = os.path.join(settings.LOCAL_STORAGE_PATH, "tenants", tenant_id, document.storage_path)
            
            # 4. Parse text
            await doc_repo.update_job_status(job, JobStatus.RUNNING, progress=20)
            text = await ParserService.parse_file(full_local_path, document.file_type)
            
            if not text:
                raise ValueError("Extracted text is empty")

            # 5. Chunk text
            await doc_repo.update_job_status(job, JobStatus.RUNNING, progress=40)
            chunking_service = ChunkingService()
            chunks = await chunking_service.split_text(text)
            
            # 6. Generate embeddings
            await doc_repo.update_job_status(job, JobStatus.RUNNING, progress=60)
            embedding_service = EmbeddingService()
            texts = [c["content"] for c in chunks]
            embeddings = await embedding_service.get_embeddings(texts)

            # 7. Upsert to Qdrant
            await doc_repo.update_job_status(job, JobStatus.RUNNING, progress=80)
            vector_service = VectorService()
            collection = await col_repo.get_by_uuid(tenant_id, document.collection_uuid)
            
            # Ensure collection exists in Qdrant
            await vector_service.ensure_collection(
                collection.vector_collection_name, 
                embedding_service.get_dimension()
            )

            points = []
            chunks_to_save = []
            
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                vector_id = str(uuid.uuid4())
                
                # Prepare Qdrant payload as per PRD Section 12.2
                payload = {
                    "tenant_uuid": tenant_id,
                    "collection_uuid": document.collection_uuid,
                    "document_uuid": document.document_uuid,
                    "chunk_uuid": vector_id, # Re-using for chunk ref
                    "external_document_id": document.external_document_id,
                    "source_type": "document",
                    "metadata": document.metadata_ or {},
                    "chunk_index": chunk["index"],
                    "token_count": chunk["token_count"]
                }
                
                points.append({
                    "id": vector_id,
                    "vector": vector,
                    "payload": payload
                })
                
                chunks_to_save.append({
                    "tenant_uuid": tenant_id,
                    "collection_uuid": document.collection_uuid,
                    "document_uuid": document.document_uuid,
                    "index": chunk["index"],
                    "content": chunk["content"],
                    "token_count": chunk["token_count"],
                    "vector_id": vector_id,
                    "metadata": document.metadata_
                })

            await vector_service.upsert_vectors(collection.vector_collection_name, points)

            # 8. Save chunk metadata to MySQL
            await doc_repo.save_chunks(chunks_to_save)

            # 9. Update final status
            await doc_repo.update_document_status(
                document, 
                DocumentStatus.INDEXED, 
                total_chunks=len(chunks)
            )
            await doc_repo.update_job_status(job, JobStatus.SUCCESS, progress=100)
            
            logger.info("process_document_task_success", doc_uuid=document_uuid, chunks=len(chunks))
            return True

        except Exception as e:
            logger.exception("process_document_task_failed", error=str(e))
            await doc_repo.update_job_status(job, JobStatus.FAILED, error=str(e))
            await doc_repo.update_document_status(document, DocumentStatus.FAILED)
            return False
