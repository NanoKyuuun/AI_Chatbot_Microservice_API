import os
import shutil
from typing import BinaryIO
from app.providers.storage.base import StorageProvider
from app.core.config import settings
from app.core.logging import logger

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = None):
        self.base_path = base_path or settings.LOCAL_STORAGE_PATH

    def _get_tenant_dir(self, tenant_id: str) -> str:
        """Get the absolute path for a tenant's directory."""
        return os.path.join(self.base_path, "tenants", tenant_id)

    def _ensure_dir(self, path: str):
        """Ensure that a directory exists."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

    async def save_file(self, file: BinaryIO, path: str, tenant_id: str) -> str:
        """
        Save a file to local storage.
        path: relative path within the tenant directory (e.g., 'documents/original/file.pdf')
        """
        tenant_dir = self._get_tenant_dir(tenant_id)
        full_path = os.path.abspath(os.path.join(tenant_dir, path))
        
        # Security check: ensure the path is within the tenant directory
        if not full_path.startswith(os.path.abspath(tenant_dir)):
            logger.error("storage_security_violation", tenant_id=tenant_id, requested_path=path)
            raise ValueError("Invalid storage path")

        self._ensure_dir(full_path)
        
        try:
            with open(full_path, "wb") as f:
                if hasattr(file, "seek"):
                    file.seek(0)
                shutil.copyfileobj(file, f)
            
            logger.info("file_saved_locally", tenant_id=tenant_id, path=path)
            return path # Return the relative path for database storage
        except Exception as e:
            logger.exception("file_save_failed", tenant_id=tenant_id, path=path, error=str(e))
            raise

    async def get_file(self, path: str, tenant_id: str) -> BinaryIO:
        """Retrieve a file as a binary stream."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        full_path = os.path.abspath(os.path.join(tenant_dir, path))
        
        if not full_path.startswith(os.path.abspath(tenant_dir)):
            raise ValueError("Invalid storage path")

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")

        return open(full_path, "rb")

    async def delete_file(self, path: str, tenant_id: str) -> bool:
        """Delete a file from local storage."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        full_path = os.path.abspath(os.path.join(tenant_dir, path))
        
        if not full_path.startswith(os.path.abspath(tenant_dir)):
            raise ValueError("Invalid storage path")

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info("file_deleted_locally", tenant_id=tenant_id, path=path)
            return True
        return False

    async def exists(self, path: str, tenant_id: str) -> bool:
        """Check if a file exists locally."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        full_path = os.path.abspath(os.path.join(tenant_dir, path))
        
        if not full_path.startswith(os.path.abspath(tenant_dir)):
            return False
            
        return os.path.exists(full_path)
