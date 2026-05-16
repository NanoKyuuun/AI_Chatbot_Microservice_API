from app.providers.llm.base import LLMProvider
from app.providers.llm.openrouter import OpenRouterProvider

def get_llm_provider(provider_type: str = "openrouter") -> LLMProvider:
    """
    Factory to get the configured LLM provider.
    """
    if provider_type == "openrouter":
        return OpenRouterProvider()
    else:
        # Default to openrouter for now
        return OpenRouterProvider()
