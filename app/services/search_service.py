from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.db.repositories.collection_repository import CollectionRepository
from app.db.repositories.document_repository import DocumentRepository
from app.schemas.search import SemanticSearchRequest, SearchResult
from app.core.errors import AppError
from fastapi import status
from app.core.logging import logger

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.col_repo = CollectionRepository(db)
        self.doc_repo = DocumentRepository(db)

    async def semantic_search(
        self, 
        tenant_id: str, 
        request: SemanticSearchRequest
    ) -> List[SearchResult]:
        # 1. Verify collection exists and belongs to tenant
        collection = await self.col_repo.get_by_uuid(tenant_id, request.collection_uuid)
        if not collection:
            raise AppError(
                code="COLLECTION_NOT_FOUND",
                message=f"Collection {request.collection_uuid} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # 2. Generate embedding for query
        query_vectors = await self.embedding_service.get_embeddings([request.query])
        query_vector = query_vectors[0]

        # 3. Prepare filters
        filters = request.filters or {}
        filters["tenant_uuid"] = tenant_id
        filters["collection_uuid"] = request.collection_uuid
        
        if request.allowed_document_ids:
            # Add filter for multiple document IDs
            filters["document_uuid"] = request.allowed_document_ids

        # 4. Search in Qdrant
        search_hits = await self.vector_service.search_vectors(
            collection_name=collection.vector_collection_name,
            query_vector=query_vector,
            limit=request.top_k,
            filters=filters
        )

        # 5. Format results
        results = []
        for hit in search_hits:
            payload = hit["payload"]
            
            result = SearchResult(
                chunk_uuid=payload.get("chunk_uuid") or hit["id"],
                document_uuid=payload.get("document_uuid"),
                title=payload.get("document_title"),
                score=hit["score"],
                content=payload.get("content") if request.include_content else None,
                metadata=payload.get("metadata"),
                page_number=payload.get("page_number"),
            )
            results.append(result)

        return results
