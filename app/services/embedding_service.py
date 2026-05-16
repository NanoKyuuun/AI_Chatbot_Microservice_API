from typing import List, Tuple, Dict, Any
from app.providers.embedding import get_embedding_provider
from app.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.provider = get_embedding_provider()

    async def get_embeddings(self, texts: List[str]) -> Tuple[List[List[float]], Dict[str, Any]]:
        """
        Get embeddings for a list of texts.
        Handles large batches if necessary.
        """
        if not texts:
            return [], {"total_tokens": 0, "prompt_tokens": 0}
            
        # Optional: chunk the texts into smaller batches if the provider has limits (e.g. 100 per request)
        batch_size = 100
        all_embeddings = []
        total_usage = {"total_tokens": 0, "prompt_tokens": 0}
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings, usage = await self.provider.get_embeddings(batch)
            all_embeddings.extend(embeddings)
            
            # Aggregate usage
            total_usage["total_tokens"] += usage.get("total_tokens", 0)
            total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            
        return all_embeddings, total_usage

    def get_dimension(self) -> int:
        return self.provider.get_dimension()
