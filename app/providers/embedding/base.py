from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of strings."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the dimension of the embeddings produced."""
        pass
