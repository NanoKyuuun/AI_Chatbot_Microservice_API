import httpx
from typing import List, Tuple, Dict, Any
from app.providers.embedding.base import EmbeddingProvider
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import AppError
from fastapi import status

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self, 
        api_key: str = None, 
        model: str = None,
        base_url: str = "https://api.openai.com/v1"
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY # Often compatible
        self.model = model or settings.EMBEDDING_MODEL
        self.base_url = base_url
        self.dimension = 1536 # Default for text-embedding-3-small

    async def get_embeddings(self, texts: List[str]) -> Tuple[List[List[float]], Dict[str, Any]]:
        logger.info("requesting_embeddings", count=len(texts), model=self.model)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": texts,
            "model": self.model
        }
        
        # Determine URL (OpenRouter vs OpenAI)
        url = f"{self.base_url}/embeddings"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error("embedding_api_error", status_code=response.status_code, body=response.text)
                    raise AppError(
                        code="EMBEDDING_API_ERROR",
                        message=f"Embedding provider returned error: {response.status_code}",
                        status_code=status.HTTP_502_BAD_GATEWAY
                    )
                
                data = response.json()
                # Sort by index to ensure order matches input
                embeddings_data = sorted(data["data"], key=lambda x: x["index"])
                embeddings = [item["embedding"] for item in embeddings_data]
                
                usage = data.get("usage", {
                    "total_tokens": 0,
                    "prompt_tokens": 0
                })
                
                return embeddings, usage
                
        except httpx.HTTPError as e:
            logger.exception("embedding_request_failed", error=str(e))
            raise AppError(
                code="EMBEDDING_REQUEST_FAILED",
                message="Failed to connect to embedding provider",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    def get_dimension(self) -> int:
        return self.dimension
