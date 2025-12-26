"""
Alerts API Endpoints
Provides AI Highlights and alert-related functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Any, Dict, List
from app.services.ai_highlights import ai_highlights_service
from app.services.market_service import market_service


router = APIRouter()


@router.get("/highlights")
async def get_ai_highlights() -> Dict[str, Any]:
    """
    Get AI-generated highlights including bullish/bearish signals and risk alerts.
    Analyzes current market data to provide actionable insights.
    """
    try:
        # Get current market data
        coins = await market_service.get_all_coins()
        
        if not coins or len(coins) == 0:
            # Return empty state if no market data
            return {
                "bullish_signals": [],
                "bearish_signals": [],
                "risk_alerts": [],
                "total_analyzed": 0,
                "generated_at": None,
                "message": "No market data available"
            }
        
        # Generate highlights from market data
        highlights = ai_highlights_service.get_highlights(coins, limit=4)
        
        return highlights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI highlights: {str(e)}"
        )


@router.get("/signals/{coin_id}")
async def get_coin_signal(coin_id: str) -> Dict[str, Any]:
    """
    Get AI signal for a specific coin.
    """
    try:
        # Get coin data
        coins = await market_service.get_all_coins()
        coin = next((c for c in coins if c.get("coin_id") == coin_id or c.get("id") == coin_id), None)
        
        if not coin:
            raise HTTPException(status_code=404, detail=f"Coin {coin_id} not found")
        
        # Generate signal
        signal = ai_highlights_service.analyze_coin_signal(coin)
        risk = ai_highlights_service.analyze_volatility_risk(coin)
        
        return {
            "signal": signal,
            "risk": risk
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze coin: {str(e)}"
        )
