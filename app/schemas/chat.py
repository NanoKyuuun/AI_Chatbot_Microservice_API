from pydantic import Field
from typing import Optional, List, Dict, Any
from app.schemas.collection import BaseSchema
from app.schemas.search import SearchResult

class ChatRequestOptions(BaseSchema):
    model: Optional[str] = None
    temperature: float = 0.2
    top_k: int = 5
    max_tokens: Optional[int] = None
    with_sources: bool = True
    answer_style: str = "simple"

class ChatRequest(BaseSchema):
    session_uuid: Optional[str] = Field(None, description="Existing session UUID or null to create new")
    collection_uuid: str = Field(..., description="Collection UUID to use for RAG")
    external_user_id: Optional[str] = Field(None, description="User ID from client application")
    message: str = Field(..., min_length=1, description="User question")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters for retrieval")
    allowed_document_ids: Optional[List[str]] = Field(None, description="Restrict search to these documents")
    options: ChatRequestOptions = Field(default_factory=ChatRequestOptions)

class ChatUsage(BaseSchema):
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseSchema):
    session_uuid: str
    message_uuid: str
    answer: str
    sources: Optional[List[SearchResult]] = None
    usage: ChatUsage
