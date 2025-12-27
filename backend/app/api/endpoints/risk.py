"""
AI Risk Assessment API Endpoints
With caching and mock fallback for demo
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException

from app.services.ai_risk import ai_risk_service
from app.services.database import get_db_service, DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory cache
_risk_cache = {
    "top_risky": {"data": None, "expires": None},
    "overview": {"data": None, "expires": None},
}
CACHE_TTL = timedelta(minutes=5)


def _get_cached(key: str):
    """Get cached data if not expired."""
    cache = _risk_cache.get(key)
    if cache and cache["data"] and cache["expires"]:
        if datetime.utcnow() < cache["expires"]:
            return cache["data"]
    return None


def _set_cache(key: str, data):
    """Set cache with TTL."""
    _risk_cache[key] = {
        "data": data,
        "expires": datetime.utcnow() + CACHE_TTL
    }


def _get_mock_risk_data():
    """Return mock risk data for demo/fallback."""
    return [
        {"coin_id": "xrp", "symbol": "XRP", "risk_score": 92, "risk_level": "LAWSUIT", "risk_label": "Lawsuit"},
        {"coin_id": "solana", "symbol": "SOL", "risk_score": 91, "risk_level": "LAWSUIT", "risk_label": "Lawsuit"},
        {"coin_id": "dogecoin", "symbol": "DOGE", "risk_score": 78, "risk_level": "EXTREME", "risk_label": "Extreme"},
        {"coin_id": "shiba-inu", "symbol": "SHIB", "risk_score": 72, "risk_level": "VOLATILE", "risk_label": "Volatile"},
        {"coin_id": "pepe", "symbol": "PEPE", "risk_score": 68, "risk_level": "VOLATILE", "risk_label": "Volatile"},
        {"coin_id": "ethereum", "symbol": "ETH", "risk_score": 35, "risk_level": "LOW_RISK", "risk_label": "Low Risk"},
        {"coin_id": "bitcoin", "symbol": "BTC", "risk_score": 28, "risk_level": "LOW_RISK", "risk_label": "Low Risk"},
        {"coin_id": "tether", "symbol": "USDT", "risk_score": 5, "risk_level": "NO_RISK", "risk_label": "No Risk"},
    ]


@router.get("/top/risky")
async def get_top_risky_coins(
    limit: int = 10,
    db: DatabaseService = Depends(get_db_service),
):
    """Get top riskiest coins. Returns mock data for now (DB perf issue)."""
    cached = _get_cached("top_risky")
    if cached:
        return cached[:limit]
    
    # Return mock data immediately (TODO: fix db.get_market_data performance)
    mock_data = _get_mock_risk_data()
    _set_cache("top_risky", mock_data)
    return mock_data[:limit]


@router.get("/overview/market")
async def get_market_risk_overview(
    db: DatabaseService = Depends(get_db_service),
):
    """Get market risk overview. Returns mock for now."""
    cached = _get_cached("overview")
    if cached:
        return cached
    
    overview = {
        "average_risk": 55,
        "risk_level": "MED_RISK",
        "risk_label": "Med Risk",
        "distribution": {
            "NO_RISK": 2,
            "SAFE": 3,
            "LOW_RISK": 5,
            "MED_RISK": 8,
            "VOLATILE": 4,
            "EXTREME": 2,
            "LAWSUIT": 2,
        },
        "top_risks": _get_mock_risk_data()[:5],
    }
    _set_cache("overview", overview)
    return overview


@router.get("/batch")
async def get_batch_risk(
    coin_ids: str,
    db: DatabaseService = Depends(get_db_service),
):
    """Get risk for multiple coins."""
    ids = [c.strip() for c in coin_ids.split(",") if c.strip()]
    if not ids:
        return []
    
    results = []
    for coin_id in ids[:10]:
        coin = db.get_coin_by_id(coin_id)
        if coin:
            risk = ai_risk_service.calculate_risk_score(coin)
            results.append(risk)
    return results


@router.get("/{coin_id}")
async def get_coin_risk(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service),
):
    """Get risk for a specific coin."""
    coin = db.get_coin_by_id(coin_id)
    if not coin:
        raise HTTPException(status_code=404, detail=f"Coin {coin_id} not found")
    return ai_risk_service.calculate_risk_score(coin)
