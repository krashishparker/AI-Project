import redis
import json
from typing import Optional, Any
from app.core.config import settings

# Create Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)


class RedisCache:
    """Redis cache wrapper for common operations."""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        try:
            redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete value from cache."""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
