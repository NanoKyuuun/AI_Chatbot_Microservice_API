from datetime import datetime
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ResponseMeta(BaseModel):
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StandardResponse(BaseSchema, Generic[T]):
    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

class CollectionBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    metadata_schema: Optional[dict[str, Any]] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    metadata_schema: Optional[dict[str, Any]] = None
    status: Optional[str] = None

class CollectionRead(CollectionBase):
    collection_uuid: str
    vector_collection_name: str
    status: str
    created_at: datetime
    updated_at: datetime
