"""
Admin Settings Service
Redis-based persistence for admin settings
"""

import json
import logging
from typing import Dict, Any, Optional

import redis
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class BackendSettings(BaseModel):
    coingecko_api_key: str = ""
    etherscan_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    market_sync_interval: int = 60
    ai_analysis_interval: int = 300
    onchain_sync_interval: int = 600


class FrontendSettings(BaseModel):
    site_name: str = "AI Crypto Hub"
    banner_image_url: str = ""
    announcement_text: str = ""
    maintenance_mode: bool = False
    meta_title: str = "AI Crypto Hub - Cryptocurrency Analytics"
    meta_description: str = "Real-time cryptocurrency market data with AI-powered analysis"


class AISettings(BaseModel):
    system_prompt: str = "You are an AI cryptocurrency analyst. Analyze the provided market data and sentiment indicators to provide trading signals."
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    whale_threshold: int = 100000
    sentiment_weight: int = 40


class SettingsService:
    """Service for managing admin settings with Redis persistence"""
    
    BACKEND_KEY = "admin:settings:backend"
    FRONTEND_KEY = "admin:settings:frontend"
    AI_KEY = "admin:settings:ai"
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._fallback_cache: Dict[str, Any] = {}
    
    @property
    def redis(self) -> Optional[redis.Redis]:
        """Lazy load Redis connection"""
        if self._redis is None:
            try:
                settings = get_settings()
                redis_url = getattr(settings, 'redis_url', None) or "redis://localhost:6379"
                self._redis = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self._redis.ping()
                logger.info("Redis connection established for settings")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory fallback: {e}")
                self._redis = None
        return self._redis
    
    def _get(self, key: str) -> Optional[str]:
        """Get value from Redis or fallback cache"""
        if self.redis:
            try:
                return self.redis.get(key)
            except Exception as e:
                logger.error(f"Redis GET failed: {e}")
        return self._fallback_cache.get(key)
    
    def _set(self, key: str, value: str) -> bool:
        """Set value in Redis and fallback cache"""
        self._fallback_cache[key] = value
        if self.redis:
            try:
                self.redis.set(key, value)
                return True
            except Exception as e:
                logger.error(f"Redis SET failed: {e}")
        return False
    
    # Backend Settings
    def get_backend_settings(self) -> BackendSettings:
        """Get backend settings"""
        data = self._get(self.BACKEND_KEY)
        if data:
            try:
                return BackendSettings(**json.loads(data))
            except:
                pass
        return BackendSettings()
    
    def save_backend_settings(self, settings: BackendSettings) -> bool:
        """Save backend settings"""
        return self._set(self.BACKEND_KEY, settings.model_dump_json())
    
    def get_backend_settings_masked(self) -> Dict[str, Any]:
        """Get backend settings with masked API keys"""
        settings = self.get_backend_settings().model_dump()
        for key in ["coingecko_api_key", "etherscan_api_key", "gemini_api_key", "deepseek_api_key"]:
            if settings.get(key):
                val = settings[key]
                settings[key] = "***" + val[-4:] if len(val) > 4 else "***"
        return settings
    
    # Frontend Settings
    def get_frontend_settings(self) -> FrontendSettings:
        """Get frontend settings"""
        data = self._get(self.FRONTEND_KEY)
        if data:
            try:
                return FrontendSettings(**json.loads(data))
            except:
                pass
        return FrontendSettings()
    
    def save_frontend_settings(self, settings: FrontendSettings) -> bool:
        """Save frontend settings"""
        return self._set(self.FRONTEND_KEY, settings.model_dump_json())
    
    # AI Settings
    def get_ai_settings(self) -> AISettings:
        """Get AI tuning settings"""
        data = self._get(self.AI_KEY)
        if data:
            try:
                return AISettings(**json.loads(data))
            except:
                pass
        return AISettings()
    
    def save_ai_settings(self, settings: AISettings) -> bool:
        """Save AI settings"""
        return self._set(self.AI_KEY, settings.model_dump_json())


# Singleton instance
_settings_service: Optional[SettingsService] = None


def get_settings_service() -> SettingsService:
    """Get settings service instance"""
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service
