import pytest
from unittest.mock import patch, MagicMock

def test_upload_document_flow(client):
    # Mock DocumentService.upload_document
    mock_document = MagicMock()
    mock_document.document_uuid = "test-doc-uuid"
    mock_document.status = "pending"
    
    mock_job = MagicMock()
    mock_job.job_uuid = "test-job-uuid"
    
    with patch("app.api.v1.routes_documents.DocumentService.upload_document") as mock_upload:
        mock_upload.return_value = (mock_document, mock_job)
        
        response = client.post(
            "/v1/documents",
            data={
                "collection_uuid": "test-coll-uuid",
                "title": "Test Document"
            },
            files={"file": ("test.txt", b"Hello World", "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["document_uuid"] == "test-doc-uuid"
        assert data["job_uuid"] == "test-job-uuid"
        assert data["status"] == "pending"
