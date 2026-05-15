from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class StorageProvider(ABC):
    @abstractmethod
    async def save_file(self, file: BinaryIO, path: str, tenant_id: str) -> str:
        """Save a file and return the storage path or URL."""
        pass

    @abstractmethod
    async def get_file(self, path: str, tenant_id: str) -> BinaryIO:
        """Retrieve a file as a binary stream."""
        pass

    @abstractmethod
    async def delete_file(self, path: str, tenant_id: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    async def exists(self, path: str, tenant_id: str) -> bool:
        """Check if a file exists."""
        pass
