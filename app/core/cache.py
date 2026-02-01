import asyncio
import json
from typing import Any, Callable, Optional

from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

from app.core.config import settings

redis_client: Optional[Redis] = None

async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

async def get_cached_data(
    key: str,
    fetch_func: Callable[..., Any],
    ttl: int = 300
) -> Any:
    """
    Get data from cache or fetch it from source if missing.

    Args:
        key: Cache key
        fetch_func: Function to fetch data if cache miss (can be sync or async)
        ttl: Time to live in seconds
    """
    redis = await get_redis()
    try:
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        # Log error but fall back to source. In production, use proper logger.
        print(f"Cache get error: {e}")
        pass

    # Fetch data
    if asyncio.iscoroutinefunction(fetch_func):
        data = await fetch_func()
    else:
        # Run synchronous blocking functions in a threadpool to avoid blocking the event loop
        data = await run_in_threadpool(fetch_func)

    try:
        # Use default=str to handle non-serializable types like dates/decimals
        await redis.set(key, json.dumps(data, default=str), ex=ttl)
    except Exception as e:
        print(f"Cache set error: {e}")

    return data
