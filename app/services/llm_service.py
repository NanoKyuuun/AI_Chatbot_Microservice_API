from typing import List, Dict, Any, Optional
from app.providers.llm import get_llm_provider
from app.core.logging import logger

class LLMService:
    def __init__(self, provider_type: str = "openrouter"):
        self.provider = get_llm_provider(provider_type)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the configured LLM provider.
        """
        logger.info("generating_llm_response", model=model, message_count=len(messages))
        
        return await self.provider.generate_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
