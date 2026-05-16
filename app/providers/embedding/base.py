from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any

class EmbeddingProvider(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> Tuple[List[List[float]], Dict[str, Any]]:
        """
        Generate embeddings for a list of strings.
        Returns a tuple of (embeddings, usage_dict).
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the dimension of the embeddings produced."""
        pass
