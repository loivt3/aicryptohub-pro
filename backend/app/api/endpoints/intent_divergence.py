"""
Intent Divergence API Endpoints
Shadow Analysis Engine for whale-crowd divergence detection
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from app.services.database import DatabaseService, get_database_service
from app.services.analyzer import AnalyzerService
from app.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intent-divergence", tags=["Intent Divergence"])


@router.get("/{coin_id}")
async def get_intent_divergence(
    coin_id: str,
    include_ai: bool = True,
    db: DatabaseService = Depends(get_database_service),
    settings: Settings = Depends(get_settings),
):
    """
    Get intent divergence analysis for a coin.
    
    Detects divergence between crowd sentiment and whale behavior:
    - Shadow Accumulation: Crowd fearful, whales accumulating
    - Bull Trap: Crowd greedy, whales distributing
    
    Args:
        coin_id: Coin identifier (e.g., 'bitcoin')
        include_ai: Generate AI Shadow Insight
        
    Returns:
        Complete divergence package for frontend
    """
    try:
        analyzer = AnalyzerService(db, settings)
        result = await analyzer.calculate_intent_divergence_v2(
            coin_id,
            include_ai_insight=include_ai,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get intent divergence for {coin_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_divergence_history(
    coin_id: Optional[str] = None,
    limit: int = 10,
    db: DatabaseService = Depends(get_database_service),
):
    """
    Get recent intent divergence signals.
    
    Args:
        coin_id: Optional filter by coin
        limit: Max results (default 10)
        
    Returns:
        List of recent divergence logs
    """
    from sqlalchemy import text
    
    try:
        if coin_id:
            query = text("""
                SELECT 
                    id, coin_id, symbol, timestamp,
                    sentiment_score, whale_score, divergence_type,
                    intent_score, shadow_insight
                FROM intent_divergence_logs
                WHERE coin_id = :coin_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """)
            params = {"coin_id": coin_id, "limit": limit}
        else:
            query = text("""
                SELECT 
                    id, coin_id, symbol, timestamp,
                    sentiment_score, whale_score, divergence_type,
                    intent_score, shadow_insight
                FROM intent_divergence_logs
                WHERE divergence_type != 'neutral'
                ORDER BY timestamp DESC
                LIMIT :limit
            """)
            params = {"limit": limit}
        
        with db.engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()
            
            return [
                {
                    "id": r[0],
                    "coin_id": r[1],
                    "symbol": r[2],
                    "timestamp": r[3].isoformat() if r[3] else None,
                    "sentiment_score": r[4],
                    "whale_score": r[5],
                    "divergence_type": r[6],
                    "intent_score": r[7],
                    "shadow_insight": r[8],
                    "divergence_label": format_divergence_type(r[6]),
                }
                for r in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get divergence history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar/{coin_id}")
async def get_radar_data(
    coin_id: str,
    db: DatabaseService = Depends(get_database_service),
    settings: Settings = Depends(get_settings),
):
    """
    Get radar chart data for ShadowRadar component.
    
    Returns 5-axis data:
    - Crowd Sentiment
    - Whale Momentum
    - Exchange Pressure
    - Network Growth
    - Intent Strength
    """
    try:
        analyzer = AnalyzerService(db, settings)
        
        # Get divergence data
        divergence = await analyzer.calculate_intent_divergence_v2(
            coin_id,
            include_ai_insight=False,
        )
        
        # Convert whale flow to exchange pressure (0-100)
        whale_flow = divergence.get("whale_net_flow_usd", 0)
        exchange_pressure = 50 - (whale_flow / 100000) * 50
        exchange_pressure = max(0, min(100, exchange_pressure))
        
        # Get network growth from DAU (placeholder - would come from onchain_signals)
        network_growth = 50  # Default
        
        radar = analyzer.get_radar_data(
            sentiment_score=divergence.get("sentiment_score", 50),
            whale_score=divergence.get("whale_score", 50),
            exchange_pressure=exchange_pressure,
            network_growth=network_growth,
            intent_score=divergence.get("intent_score", 50),
        )
        
        return {
            **radar,
            "divergence_type": divergence.get("divergence_type"),
            "divergence_label": divergence.get("divergence_label"),
        }
        
    except Exception as e:
        logger.error(f"Failed to get radar data for {coin_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def format_divergence_type(div_type: str) -> str:
    """Convert divergence type to label"""
    labels = {
        "shadow_accumulation": "Shadow Accumulation",
        "bull_trap": "Bull Trap Warning",
        "confirmation": "Trend Confirmation",
        "neutral": "No Clear Signal",
    }
    return labels.get(div_type, div_type)
