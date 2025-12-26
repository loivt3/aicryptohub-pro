"""
Alerts API Endpoints
Provides AI Highlights and alert-related functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Any, Dict, List
from app.services.ai_highlights import ai_highlights_service
from app.services.database import DatabaseService, get_db_service


router = APIRouter()


@router.get("/highlights")
async def get_ai_highlights(
    db: DatabaseService = Depends(get_db_service)
) -> Dict[str, Any]:
    """
    Get AI-generated highlights using Gemini/DeepSeek.
    Analyzes current market data to provide intelligent, actionable insights.
    Falls back to algorithmic analysis if AI is unavailable.
    """
    try:
        # Get current market data from database
        coins = db.get_market_data(limit=50, orderby="market_cap")
        
        if not coins or len(coins) == 0:
            # Return empty state if no market data
            return {
                "highlights": [],
                "total_analyzed": 0,
                "generated_at": None,
                "message": "No market data available"
            }
        
        # Generate AI-powered highlights (with fallback to algorithmic)
        highlights = await ai_highlights_service.generate_ai_highlights(coins, limit=6)
        
        return highlights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI highlights: {str(e)}"
        )


@router.get("/signals/{coin_id}")
async def get_coin_signal(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service)
) -> Dict[str, Any]:
    """
    Get AI signal for a specific coin.
    """
    try:
        # Get coin data from database
        coins = db.get_market_data(limit=100, orderby="market_cap")
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
