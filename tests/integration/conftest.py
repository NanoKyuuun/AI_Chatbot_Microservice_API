import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import validate_api_key
from app.db.session import get_db
from unittest.mock import MagicMock

@pytest.fixture
def client():
    # Mock authentication
    async def mock_validate_api_key():
        return {"tenant_id": 1, "api_key_id": 1}
    
    # Mock DB session
    async def mock_get_db():
        yield MagicMock()

    app.dependency_overrides[validate_api_key] = mock_validate_api_key
    app.dependency_overrides[get_db] = mock_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
