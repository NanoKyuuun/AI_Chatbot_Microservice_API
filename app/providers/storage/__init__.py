from app.providers.storage.local_storage import LocalStorageProvider
from app.core.config import settings

def get_storage_provider():
    """Factory to get the configured storage provider."""
    # For now, we only support local as per PRD
    if settings.STORAGE_DRIVER == "local":
        return LocalStorageProvider()
    
    # Fallback to local
    return LocalStorageProvider()
