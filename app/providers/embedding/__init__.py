from app.providers.embedding.openai_embedding import OpenAIEmbeddingProvider
from app.core.config import settings

def get_embedding_provider():
    """Factory to get the configured embedding provider."""
    # For now, default to OpenAI compatible
    return OpenAIEmbeddingProvider()
