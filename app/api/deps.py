from typing import Optional

from fastapi import Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.core.config import settings


class PaginationParams(BaseModel):
    skip: int
    limit: int


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of items to return"),
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER)
) -> bool:
    """
    Verify API key for protected endpoints.
    
    If API_KEY is not set in settings, authentication is disabled (returns True).
    If API_KEY is set, the request must include a valid API key header.
    """
    # If no API key is configured, allow all requests (development mode)
    if not settings.API_KEY:
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return True


async def optional_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER)
) -> Optional[str]:
    """
    Optional API key verification - returns the key if valid, None if not provided.
    Does not raise an error if key is missing.
    """
    if not x_api_key:
        return None
    
    if settings.API_KEY and x_api_key == settings.API_KEY:
        return x_api_key
    
    return None


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )
