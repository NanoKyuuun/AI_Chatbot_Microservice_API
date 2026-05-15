from typing import List
from app.providers.embedding import get_embedding_provider
from app.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.provider = get_embedding_provider()

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        Handles large batches if necessary.
        """
        if not texts:
            return []
            
        # Optional: chunk the texts into smaller batches if the provider has limits (e.g. 100 per request)
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = await self.provider.get_embeddings(batch)
            all_embeddings.extend(embeddings)
            
        return all_embeddings

    def get_dimension(self) -> int:
        return self.provider.get_dimension()
