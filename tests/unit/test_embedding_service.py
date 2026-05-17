import pytest
from app.services.embedding_service import EmbeddingService
from app.providers.embedding.fastembed_provider import FastEmbedProvider

@pytest.mark.asyncio
async def test_embedding_service_local():
    service = EmbeddingService()
    # Should be FastEmbedProvider by default now
    assert isinstance(service.provider, FastEmbedProvider)
    
    texts = ["Hello world", "This is a test"]
    embeddings, usage = await service.get_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == service.get_dimension()
    assert usage["total_tokens"] == 0 # Local provider returns 0 for now
