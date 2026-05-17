from typing import List, Tuple, Dict, Any
from fastembed import TextEmbedding
from app.providers.embedding.base import EmbeddingProvider
from app.core.config import settings
from app.core.logging import logger

class FastEmbedProvider(EmbeddingProvider):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.info("initializing_fastembed", model=self.model_name)
        self.model = TextEmbedding(model_name=self.model_name)
        
        # Get dimension by embedding a dummy text
        dummy_embedding = list(self.model.embed(["dummy"]))[0]
        self.dimension = len(dummy_embedding)
        logger.info("fastembed_initialized", dimension=self.dimension)

    async def get_embeddings(self, texts: List[str]) -> Tuple[List[List[float]], Dict[str, Any]]:
        logger.info("requesting_local_embeddings", count=len(texts), model=self.model_name)
        
        # FastEmbed embed() returns a generator of numpy arrays
        embeddings_generator = self.model.embed(texts)
        embeddings = [list(e) for e in embeddings_generator]
        
        # Local embedding doesn't really have "tokens" in the same way API does, 
        # but we can return empty usage or estimate it.
        usage = {
            "total_tokens": 0,
            "prompt_tokens": 0
        }
        
        return embeddings, usage

    def get_dimension(self) -> int:
        return self.dimension
