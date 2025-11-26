import json
from typing import Any, Optional
from .redis_client import get_redis
import os

# Час життя кешу з .env або за замовчуванням
REDIS_TTL = int(os.getenv("REDIS_TTL", "60"))

async def cache_get(key: str) -> Optional[Any]:
    """Get data from cache by key"""
    redis = get_redis()
    try:
        cached_data = await redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"❌ Cache get error: {e}")
        return None
    finally:
        await redis.close()

async def cache_set(key: str, data: Any, ttl: int = REDIS_TTL) -> bool:
    """Set data to cache with TTL"""
    redis = get_redis()
    try:
        await redis.set(key, json.dumps(data), ex=ttl)
        return True
    except Exception as e:
        print(f"❌ Cache set error: {e}")
        return False
    finally:
        await redis.close()