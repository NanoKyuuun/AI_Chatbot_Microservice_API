from fastapi import Security, HTTPException, status, Header
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def validate_api_key(
    api_key: str = Security(api_key_header),
    x_tenant_id: str = Header(None)
):
    """
    Dependency to validate API key and Tenant ID.
    Note: For MVP, we will perform a simple check if the API key starts with the expected prefix
    and if the tenant ID is provided. Real database validation will be added after models are ready.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing",
        )
    
    # Extract token from 'Bearer <token>' format
    if api_key.startswith("Bearer "):
        api_key = api_key.replace("Bearer ", "")
    
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X-Tenant-ID header missing",
        )

    # TODO: Implement real database validation for API Key and Tenant UUID
    # For now, we allow any key for development if it starts with 'sk_'
    if not api_key.startswith("sk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key format",
        )

    return {"api_key": api_key, "tenant_id": x_tenant_id}
