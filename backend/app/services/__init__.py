"""
Backend Services Package

All services ported from ai-hub-pro/python-service
"""

from app.services.database import DatabaseService, get_db_service
from app.services.analyzer import AnalyzerService
from app.services.cache import CacheService, get_cache_service

__all__ = [
    # Database
    "DatabaseService",
    "get_db_service",
    
    # Analysis
    "AnalyzerService",
    
    # Caching
    "CacheService",
    "get_cache_service",
]

# Lazy imports for optional services
def get_gemini_service():
    from app.services.gemini import GeminiService
    return GeminiService

def get_deepseek_service():
    from app.services.deepseek import DeepSeekService
    return DeepSeekService

def get_data_fetcher():
    from app.services.data_fetcher import get_data_fetcher as _get_fetcher
    return _get_fetcher()

def get_onchain_collector():
    from app.services.onchain_collector import OnChainCollector
    return OnChainCollector

def get_price_aggregator():
    from app.services.price_aggregator import get_price_aggregator as _get_aggregator
    return _get_aggregator()
