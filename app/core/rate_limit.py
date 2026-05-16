import time
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from app.core.redis import get_redis
from app.core.config import settings
from app.core.logging import logger

class RateLimiter:
    def __init__(
        self, 
        limit: int, 
        window_seconds: int = 60,
        key_prefix: str = "api"
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix

    async def is_allowed(self, identifier: str) -> bool:
        """
        Check if the request is allowed for the given identifier.
        Uses Redis fixed-window counter.
        """
        try:
            redis = await get_redis()
            # Window key based on current time (e.g. per minute)
            window_id = int(time.time()) // self.window_seconds
            key = f"rl:{self.key_prefix}:{identifier}:{window_id}"
            
            async with redis.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, self.window_seconds + 5)
                results = await pipe.execute()
                
            count = results[0]
            return count <= self.limit
        except Exception as e:
            logger.error("rate_limit_error", error=str(e))
            # Fallback: allow request if Redis is down
            return True

class RateLimitChecker:
    """
    FastAPI dependency to enforce rate limits.
    """
    def __init__(self, limit: int, prefix: str = "api"):
        self.limiter = RateLimiter(limit=limit, key_prefix=prefix)

    async def __call__(self, request: Request):
        # Identify the user (API Key + Tenant ID)
        # We assume validate_api_key has already been called or we extract it here
        # For better integration, we can get it from request.state if we set it in a middleware
        # Or just extract from headers again.
        
        auth_header = request.headers.get("Authorization")
        tenant_id = request.headers.get("X-Tenant-ID")
        
        if not auth_header or not tenant_id:
            # If auth is missing, we don't rate limit here (let validate_api_key handle it)
            # but usually rate limit should come AFTER auth
            return

        identifier = f"{tenant_id}:{auth_header}"
        
        if not await self.limiter.is_allowed(identifier):
            logger.warning("rate_limit_exceeded", identifier=identifier, prefix=self.limiter.key_prefix)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMITED",
                    "message": f"Rate limit exceeded for {self.limiter.key_prefix} requests. Please try again later."
                }
            )

# Pre-defined checkers
general_rate_limit = RateLimitChecker(
    limit=settings.RATE_LIMIT_PER_MINUTE, 
    prefix="general"
)
chat_rate_limit = RateLimitChecker(
    limit=settings.CHAT_RATE_LIMIT_PER_MINUTE, 
    prefix="chat"
)
upload_rate_limit = RateLimitChecker(
    limit=settings.UPLOAD_RATE_LIMIT_PER_MINUTE, 
    prefix="upload"
)
