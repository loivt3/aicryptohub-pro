"""
Realtime Router - Real-time market data streaming endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("/status")
async def get_realtime_status() -> Dict[str, Any]:
    """
    Get real-time streamer status.
    Returns WebSocket connection state and stats.
    """
    try:
        from app.services.streamer import get_market_streamer
        streamer = get_market_streamer()
        return streamer.get_status()
    except Exception as e:
        logger.error(f"Failed to get streamer status: {e}")
        return {
            "running": False,
            "connected": False,
            "error": str(e),
        }


@router.get("/prices")
async def get_realtime_prices() -> Dict[str, Any]:
    """
    Get all cached real-time prices.
    Returns prices from Binance WebSocket stream.
    """
    try:
        from app.services.streamer import get_market_streamer
        streamer = get_market_streamer()
        prices = streamer.get_all_prices()
        
        return {
            "success": True,
            "count": len(prices),
            "prices": prices,
        }
    except Exception as e:
        logger.error(f"Failed to get prices: {e}")
        return {
            "success": False,
            "count": 0,
            "prices": {},
            "error": str(e),
        }


@router.get("/price/{symbol}")
async def get_realtime_price(symbol: str) -> Dict[str, Any]:
    """
    Get real-time price for a specific symbol.
    
    Args:
        symbol: Coin symbol (e.g., 'BTC', 'ETH')
    """
    try:
        from app.services.streamer import get_market_streamer
        streamer = get_market_streamer()
        price = streamer.get_price(symbol.upper())
        
        if not price:
            raise HTTPException(
                status_code=404,
                detail=f"Price not found for {symbol}. Symbol may not be tracked."
            )
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "data": price,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_streamer() -> Dict[str, Any]:
    """
    Start the real-time market streamer.
    Connects to Binance WebSocket.
    """
    try:
        from app.services.streamer import start_streamer as _start_streamer
        await _start_streamer()
        return {
            "success": True,
            "message": "Streamer started",
        }
    except Exception as e:
        logger.error(f"Failed to start streamer: {e}")
        return {
            "success": False,
            "message": str(e),
        }


@router.post("/stop")
async def stop_streamer() -> Dict[str, Any]:
    """
    Stop the real-time market streamer.
    """
    try:
        from app.services.streamer import stop_streamer as _stop_streamer
        await _stop_streamer()
        return {
            "success": True,
            "message": "Streamer stopped",
        }
    except Exception as e:
        logger.error(f"Failed to stop streamer: {e}")
        return {
            "success": False,
            "message": str(e),
        }
