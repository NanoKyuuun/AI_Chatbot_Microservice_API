from pydantic import Field
from typing import Optional, List, Dict, Any
from app.schemas.collection import BaseSchema

class SemanticSearchRequest(BaseSchema):
    collection_uuid: str = Field(..., description="UUID of the collection to search in")
    query: str = Field(..., min_length=1, description="Text query for semantic search")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters for Qdrant")
    allowed_document_ids: Optional[List[str]] = Field(None, description="Optional list of document UUIDs to restrict search")
    include_content: bool = Field(True, description="Whether to include the text content of the chunks")

class SearchResult(BaseSchema):
    chunk_uuid: str
    document_uuid: str
    title: Optional[str] = None
    page_number: Optional[int] = None
    score: float
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SemanticSearchResponse(BaseSchema):
    results: List[SearchResult]
