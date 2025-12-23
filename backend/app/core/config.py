"""
Application Configuration
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "AI Crypto Hub Pro"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "https://aicryptohub.io",
    ]
    
    # Database
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Database pooling (for SQLAlchemy)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    redis_url: str = "redis://localhost:6379"  # alias for legacy compatibility
    
    # AI Providers
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    
    # Alias for legacy services (lowercase)
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    
    # External APIs
    COINGECKO_API_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    COVALENT_API_KEY: str = ""  # For top holder data
    MORALIS_API_KEY: str = ""   # Fallback provider
    COINMARKETCAP_API_KEY: str = ""
    CRYPTOPANIC_TOKEN: str = ""
    
    # Alias for legacy services (lowercase)
    coingecko_api_key: str = ""
    etherscan_api_key: str = ""
    covalent_api_key: str = ""
    moralis_api_key: str = ""
    cryptopanic_token: str = ""
    
    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Alias for database_url (lowercase)
    database_url: str = ""
    
    def __init__(self, **data):
        super().__init__(**data)
        # Copy uppercase values to lowercase aliases if not set
        if not self.gemini_api_key and self.GEMINI_API_KEY:
            object.__setattr__(self, 'gemini_api_key', self.GEMINI_API_KEY)
        if not self.deepseek_api_key and self.DEEPSEEK_API_KEY:
            object.__setattr__(self, 'deepseek_api_key', self.DEEPSEEK_API_KEY)
        if not self.coingecko_api_key and self.COINGECKO_API_KEY:
            object.__setattr__(self, 'coingecko_api_key', self.COINGECKO_API_KEY)
        if not self.etherscan_api_key and self.ETHERSCAN_API_KEY:
            object.__setattr__(self, 'etherscan_api_key', self.ETHERSCAN_API_KEY)
        if not self.cryptopanic_token and self.CRYPTOPANIC_TOKEN:
            object.__setattr__(self, 'cryptopanic_token', self.CRYPTOPANIC_TOKEN)
        if not self.database_url and self.DATABASE_URL:
            object.__setattr__(self, 'database_url', self.DATABASE_URL)
        if not self.redis_url and self.REDIS_URL:
            object.__setattr__(self, 'redis_url', self.REDIS_URL)
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow both uppercase and lowercase env vars
        extra = "ignore"  # Ignore extra env vars


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (for dependency injection)"""
    return Settings()

