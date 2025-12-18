"""
Market Data Endpoints - Complete Implementation
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel

from app.services.database import DatabaseService, get_db_service

router = APIRouter()


class CoinData(BaseModel):
    coin_id: str
    symbol: str
    name: str
    image: Optional[str] = None
    price: float
    change_1h: Optional[float] = None
    change_24h: float
    change_7d: Optional[float] = None
    market_cap: float
    market_cap_rank: Optional[int] = None
    volume_24h: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None


class MarketDataResponse(BaseModel):
    success: bool
    data: List[dict]
    meta: dict


@router.get("", response_model=MarketDataResponse)
async def get_market_data(
    limit: int = Query(default=100, le=500),
    orderby: str = Query(default="market_cap"),
    db: DatabaseService = Depends(get_db_service),
):
    """Get all market data from database"""
    coins = db.get_market_data(limit=limit, orderby=orderby)
    
    return MarketDataResponse(
        success=True,
        data=coins,
        meta={
            "count": len(coins),
            "timestamp": datetime.now().isoformat(),
            "source": "database",
        }
    )


@router.get("/realtime", response_model=MarketDataResponse)
async def get_market_data_realtime(
    limit: int = Query(default=200, le=500),
    db: DatabaseService = Depends(get_db_service),
):
    """Get real-time market data"""
    coins = db.get_market_data(limit=limit)
    
    return MarketDataResponse(
        success=True,
        data=coins,
        meta={
            "count": len(coins),
            "timestamp": datetime.now().isoformat(),
            "source": "realtime",
        }
    )


@router.get("/live")
async def get_live_market_data(
    db: DatabaseService = Depends(get_db_service),
):
    """Get live prices from cache/streamer"""
    coins = db.get_market_data(limit=100)
    
    return {
        "success": True,
        "data": coins,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ohlcv/{symbol}")
async def get_ohlcv_data(
    symbol: str,
    interval: str = Query(default="1h"),
    limit: int = Query(default=200, le=1000),
    db: DatabaseService = Depends(get_db_service),
):
    """Get OHLCV candlestick data for charts"""
    ohlcv = db.get_ohlcv_data(symbol.lower(), interval=interval, limit=limit)
    
    return {
        "success": True,
        "symbol": symbol.upper(),
        "interval": interval,
        "count": len(ohlcv),
        "data": ohlcv,
    }


@router.get("/stats/global")
async def get_global_market_stats():
    """Get global market statistics from CoinGecko"""
    from app.services.price_aggregator import get_price_aggregator
    
    try:
        aggregator = get_price_aggregator()
        stats = await aggregator.get_global_stats()
        
        # Also fetch Fear & Greed index
        fear_greed = await fetch_fear_greed_index()
        
        return {
            "success": True,
            "data": {
                "total_market_cap": stats.get("total_market_cap", 0),
                "total_volume_24h": stats.get("total_volume_24h", 0),
                "btc_dominance": stats.get("btc_dominance", 0),
                "eth_dominance": stats.get("eth_dominance", 0),
                "market_cap_change_24h": stats.get("market_cap_change_24h", 0),
                "active_cryptocurrencies": stats.get("active_cryptocurrencies", 0),
                "fear_greed_index": fear_greed.get("value", 50),
                "fear_greed_classification": fear_greed.get("classification", "Neutral"),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "total_market_cap": 0,
                "total_volume_24h": 0,
                "btc_dominance": 50,
                "eth_dominance": 0,
                "market_cap_change_24h": 0,
                "fear_greed_index": 50,
                "fear_greed_classification": "Neutral",
            }
        }


@router.get("/{coin_id}")
async def get_single_coin(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service),
):
    """Get data for a single coin"""
    coin = db.get_coin_by_id(coin_id)
    
    if not coin:
        return {"success": False, "error": f"Coin {coin_id} not found"}
    
    return {
        "success": True,
        "data": coin,
    }


async def fetch_fear_greed_index():
    """Fetch Fear & Greed Index from alternative.me API"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.alternative.me/fng/",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        return {
                            "value": int(data["data"][0].get("value", 50)),
                            "classification": data["data"][0].get("value_classification", "Neutral")
                        }
    except Exception as e:
        print(f"Failed to fetch Fear & Greed: {e}")
    
    return {"value": 50, "classification": "Neutral"}
