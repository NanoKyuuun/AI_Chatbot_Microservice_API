from app.providers.embedding.openai_embedding import OpenAIEmbeddingProvider
from app.providers.embedding.fastembed_provider import FastEmbedProvider
from app.core.config import settings

def get_embedding_provider():
    """Factory to get the configured embedding provider."""
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider()
    
    # Default to local (FastEmbed)
    return FastEmbedProvider()
