"""
Redis cache service for AI Hub AI Engine
Caches OHLCV data and analysis results
"""
import json
import hashlib
from typing import Any, Optional, List, Dict
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Redis client (lazy initialized)
_redis_client = None


def get_redis_client():
    """Get or create Redis client"""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        from config import get_settings
        
        settings = get_settings()
        redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        logger.info("Redis connected successfully")
        return _redis_client
        
    except ImportError:
        logger.warning("Redis not installed. Run: pip install redis")
        return None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return None


class CacheService:
    """Redis-based caching service"""
    
    # Cache TTLs
    TTL_OHLCV = timedelta(minutes=5)
    TTL_ANALYSIS = timedelta(minutes=15)
    TTL_COINS = timedelta(minutes=1)
    
    # Prefixes
    PREFIX_OHLCV = "ohlcv:"
    PREFIX_ANALYSIS = "analysis:"
    PREFIX_COINS = "coins:"
    
    def __init__(self):
        self.client = get_redis_client()
        self.enabled = self.client is not None
    
    def _make_key(self, prefix: str, *parts) -> str:
        """Create cache key"""
        key_parts = [str(p) for p in parts]
        return f"{prefix}{':'.join(key_parts)}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: timedelta = None) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False
        
        try:
            data = json.dumps(value, default=str)
            if ttl:
                self.client.setex(key, int(ttl.total_seconds()), data)
            else:
                self.client.set(key, data)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0
    
    # Specialized methods
    
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> Optional[List[Dict]]:
        """Get cached OHLCV data"""
        key = self._make_key(self.PREFIX_OHLCV, symbol, timeframe, limit)
        return self.get(key)
    
    def set_ohlcv(self, symbol: str, timeframe: str, limit: int, data: List[Dict]) -> bool:
        """Cache OHLCV data"""
        key = self._make_key(self.PREFIX_OHLCV, symbol, timeframe, limit)
        return self.set(key, data, self.TTL_OHLCV)
    
    def get_analysis(self, coin_id: str) -> Optional[Dict]:
        """Get cached analysis result"""
        key = self._make_key(self.PREFIX_ANALYSIS, coin_id)
        return self.get(key)
    
    def set_analysis(self, coin_id: str, data: Dict) -> bool:
        """Cache analysis result"""
        key = self._make_key(self.PREFIX_ANALYSIS, coin_id)
        return self.set(key, data, self.TTL_ANALYSIS)
    
    def get_coins_list(self) -> Optional[List[str]]:
        """Get cached coins list"""
        key = self._make_key(self.PREFIX_COINS, "list")
        return self.get(key)
    
    def set_coins_list(self, coins: List[str]) -> bool:
        """Cache coins list"""
        key = self._make_key(self.PREFIX_COINS, "list")
        return self.set(key, coins, self.TTL_COINS)
    
    def invalidate_analysis(self, coin_id: str = None) -> int:
        """Invalidate analysis cache"""
        if coin_id:
            key = self._make_key(self.PREFIX_ANALYSIS, coin_id)
            self.delete(key)
            return 1
        return self.clear_pattern(f"{self.PREFIX_ANALYSIS}*")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.client.info("memory")
            return {
                "enabled": True,
                "connected": True,
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "keys_count": self.client.dbsize(),
            }
        except Exception as e:
            return {"enabled": True, "connected": False, "error": str(e)}


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
