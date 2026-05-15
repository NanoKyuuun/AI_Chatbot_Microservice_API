import uuid
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document import Collection, CollectionStatus
from app.schemas.collection import CollectionCreate, CollectionUpdate

class CollectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant_id: str, obj_in: CollectionCreate) -> Collection:
        collection_uuid = str(uuid.uuid4())
        # Convention for vector collection name as per PRD
        vector_name = f"tenant_{tenant_id}_col_{collection_uuid[:8]}"
        
        db_obj = Collection(
            collection_uuid=collection_uuid,
            tenant_uuid=tenant_id,
            name=obj_in.name,
            description=obj_in.description,
            vector_collection_name=vector_name,
            metadata_schema=obj_in.metadata_schema,
            status=CollectionStatus.ACTIVE
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_uuid(self, tenant_id: str, collection_uuid: str) -> Optional[Collection]:
        query = select(Collection).where(
            Collection.tenant_uuid == tenant_id,
            Collection.collection_uuid == collection_uuid,
            Collection.status != "deleted" # Assuming we might want soft delete later, though PRD says active/inactive
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Collection]:
        query = select(Collection).where(
            Collection.tenant_uuid == tenant_id
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, db_obj: Collection, obj_in: CollectionUpdate) -> Collection:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Collection) -> None:
        # For now, literal delete, but we could do status='deleted'
        await self.db.delete(db_obj)
        await self.db.commit()
