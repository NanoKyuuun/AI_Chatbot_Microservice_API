import httpx
from typing import List, Dict, Any, Optional
from app.providers.llm.base import LLMProvider
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import AppError
from fastapi import status

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/NanoKyuuun/AI_Chatbot_Microservice_API", # Required by OpenRouter
            "X-Title": "AI Chatbot Microservice API",
            "Content-Type": "application/json"
        }

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2, # Lower default for RAG as per PRD
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        target_model = model or settings.DEFAULT_CHAT_MODEL
        
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        # Merge additional kwargs
        payload.update(kwargs)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error("openrouter_error", status_code=response.status_code, body=response.text)
                    raise AppError(
                        code="LLM_PROVIDER_ERROR",
                        message=f"OpenRouter returned error: {response.status_code}",
                        status_code=status.HTTP_502_BAD_GATEWAY
                    )
                
                data = response.json()
                
                # Format standard response as required by our services
                return {
                    "answer": data["choices"][0]["message"]["content"],
                    "model": data.get("model", target_model),
                    "usage": data.get("usage", {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }),
                    "raw_response": data # Keeping for potential debugging
                }
                
        except httpx.RequestError as e:
            logger.exception("openrouter_request_failed", error=str(e))
            raise AppError(
                code="LLM_PROVIDER_ERROR",
                message="Failed to connect to OpenRouter",
                status_code=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.exception("llm_completion_failed", error=str(e))
            raise AppError(
                code="LLM_PROVIDER_ERROR",
                message=f"LLM completion failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
