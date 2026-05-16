import pytest
from unittest.mock import patch, MagicMock

def test_chat_flow(client):
    # Mock ChatService.chat
    mock_response = {
        "session_uuid": "test-session-uuid",
        "message_uuid": "test-message-uuid",
        "answer": "AI adalah kecerdasan buatan.",
        "sources": [
            {
                "chunk_uuid": "chunk1",
                "document_uuid": "doc1",
                "title": "Doc 1",
                "content": "AI adalah...",
                "page_number": 1,
                "score": 0.9
            }
        ],
        "usage": {
            "model": "gpt-4o-mini",
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }
    
    with patch("app.api.v1.routes_chat.ChatService.chat") as mock_chat:
        mock_chat.return_value = mock_response
        
        response = client.post(
            "/v1/chat",
            json={
                "collection_uuid": "test-coll-uuid",
                "message": "Apa itu AI?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["answer"] == "AI adalah kecerdasan buatan."
        assert len(data["sources"]) == 1
        assert data["sources"][0]["chunk_uuid"] == "chunk1"
