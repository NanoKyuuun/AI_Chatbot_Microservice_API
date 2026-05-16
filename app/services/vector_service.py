from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.core.logging import logger

class VectorService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

    async def ensure_collection(self, collection_name: str, vector_size: int):
        """Ensure a Qdrant collection exists with the specified vector size."""
        collections = await self.client.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)
        
        if not exists:
            logger.info("creating_qdrant_collection", name=collection_name, size=vector_size)
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, 
                    distance=models.Distance.COSINE
                )
            )

    async def upsert_vectors(
        self, 
        collection_name: str, 
        points: List[Dict[str, Any]]
    ):
        """
        Upsert a list of vectors into Qdrant.
        points should be a list of dicts with 'id', 'vector', and 'payload'.
        """
        logger.info("upserting_vectors", collection=collection_name, count=len(points))
        
        qdrant_points = [
            models.PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"]
            ) for p in points
        ]
        
        await self.client.upsert(
            collection_name=collection_name,
            points=qdrant_points
        )

    async def search_vectors(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.
        """
        logger.info("searching_vectors", collection=collection_name, limit=limit)
        
        query_filter = None
        if filters:
            must_filters = []
            for key, value in filters.items():
                if isinstance(value, list):
                    must_filters.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchAny(any=value)
                        )
                    )
                else:
                    must_filters.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
            query_filter = models.Filter(must=must_filters)

        search_result = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            } for hit in search_result
        ]

    async def delete_vectors(self, collection_name: str, ids: List[str]):
        """Delete specific vectors by ID."""
        await self.client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=ids)
        )

    async def delete_by_filter(self, collection_name: str, filters: Dict[str, Any]):
        """Delete vectors that match a specific filter."""
        must_filters = []
        for key, value in filters.items():
            must_filters.append(
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                )
            )
            
        await self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=must_filters)
            )
        )
