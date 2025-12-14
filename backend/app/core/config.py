"""
Application Configuration
"""

from typing import List
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
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Providers
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    
    # External APIs
    COINGECKO_API_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    
    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
