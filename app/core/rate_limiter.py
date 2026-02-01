"""
Rate limiting middleware using SlowAPI.
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    Handles X-Forwarded-For header for reverse proxies.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request) or "unknown"


# Create limiter instance with Redis backend for distributed rate limiting
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds"],
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window",
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": True,
            "message": "Rate limit exceeded. Please slow down your requests.",
            "type": "RateLimitExceeded",
            "details": {
                "limit": exc.detail,
                "retry_after": getattr(exc, "retry_after", settings.RATE_LIMIT_WINDOW),
            },
        },
        headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)},
    )


# Rate limit decorators for different endpoint types
def rate_limit_standard(func):
    """Standard rate limit for most endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds")(func)


def rate_limit_strict(func):
    """Stricter rate limit for resource-intensive endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_REQUESTS // 5}/{settings.RATE_LIMIT_WINDOW}seconds")(func)


def rate_limit_relaxed(func):
    """Relaxed rate limit for read-only endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_REQUESTS * 2}/{settings.RATE_LIMIT_WINDOW}seconds")(func)
