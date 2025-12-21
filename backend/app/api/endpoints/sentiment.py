"""
AI Sentiment Endpoints - Complete Implementation
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, Depends, BackgroundTasks
from pydantic import BaseModel

from app.services.database import DatabaseService, get_db_service
from app.services.analyzer import AnalyzerService

router = APIRouter()


class SentimentData(BaseModel):
    coin_id: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    asi_score: float
    signal: str
    reason: Optional[str] = None
    provider: Optional[str] = None
    analyzed_at: Optional[datetime] = None


@router.get("", response_model=List[SentimentData])
async def get_sentiment_data(
    limit: int = Query(default=100, le=500),
    db: DatabaseService = Depends(get_db_service),
):
    """Get sentiment data for all coins"""
    data = db.get_sentiment_data(limit=limit)
    return data


@router.get("/status")
async def get_sentiment_status(
    db: DatabaseService = Depends(get_db_service),
):
    """Get AI sentiment system status"""
    data = db.get_sentiment_data(limit=1)
    
    return {
        "status": "operational",
        "last_analysis": data[0].get("analyzed_at") if data else None,
        "provider": "technical",
    }


@router.post("/analyze")
async def trigger_analysis(
    background_tasks: BackgroundTasks,
    coin_ids: List[str] = [],
    db: DatabaseService = Depends(get_db_service),
):
    """Trigger AI analysis for coins (background task)"""
    analyzer = AnalyzerService(db)
    
    async def run_analysis():
        await analyzer.analyze_coins(coin_ids)
    
    background_tasks.add_task(run_analysis)
    
    return {
        "success": True,
        "message": f"Analysis queued for {len(coin_ids)} coins",
    }


@router.get("/{coin_id}", response_model=SentimentData)
async def get_coin_sentiment(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service),
):
    """Get sentiment data for a specific coin"""
    data = db.get_coin_sentiment(coin_id)
    
    if not data:
        return SentimentData(
            coin_id=coin_id,
            asi_score=50,
            signal="NEUTRAL",
            reason="No analysis available",
        )
    
    return SentimentData(**data)


class MultiHorizonBatchRequest(BaseModel):
    coin_ids: List[str]


@router.post("/multi-horizon/batch")
async def get_multi_horizon_batch(
    request: MultiHorizonBatchRequest,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Batch fetch multi-horizon ASI for multiple coins.
    
    Returns cached data if available (< 5 min old).
    Only computes on-demand for missing coins (max 5 to prevent overload).
    
    This endpoint replaces multiple parallel calls to /{coin_id}/multi-horizon
    and significantly reduces server load.
    """
    import asyncio
    import logging
    from app.core.config import get_settings
    
    logger = logging.getLogger(__name__)
    coin_ids = request.coin_ids[:50]  # Limit to 50 coins max
    
    if not coin_ids:
        return {"success": True, "data": {}, "from_cache": 0, "computed": 0}
    
    # Check cache first
    cached = db.get_multi_horizon_cache(coin_ids, max_age_minutes=5)
    
    results = {}
    missing = []
    
    for coin_id in coin_ids:
        if coin_id in cached and cached[coin_id]:
            results[coin_id] = cached[coin_id]
        else:
            missing.append(coin_id)
    
    computed_count = 0
    
    # Compute missing coins (limit to 5 to prevent overload)
    if missing:
        settings = get_settings()
        analyzer = AnalyzerService(db, settings)
        
        # Only compute up to 5 missing coins per request
        for coin_id in missing[:5]:
            try:
                result = await asyncio.wait_for(
                    analyzer.calculate_multi_horizon_asi(coin_id, use_cache=False),
                    timeout=10.0  # Short timeout per coin
                )
                results[coin_id] = result
                computed_count += 1
            except Exception as e:
                logger.warning(f"Failed to compute multi-horizon for {coin_id}: {e}")
                # Return default values for failed coins
                results[coin_id] = {
                    "coin_id": coin_id,
                    "asi_short": 50,
                    "asi_medium": 50,
                    "asi_long": 50,
                    "asi_combined": 50,
                    "signal_short": "NEUTRAL",
                    "signal_medium": "NEUTRAL",
                    "signal_long": "NEUTRAL",
                    "signal_combined": "NEUTRAL",
                }
    
    return {
        "success": True,
        "data": results,
        "from_cache": len(cached),
        "computed": computed_count,
        "total": len(coin_ids),
    }


@router.get("/{coin_id}/multi-horizon")
async def get_multi_horizon_asi(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Get multi-horizon ASI analysis for a coin.
    
    Returns:
    - asi_short: Short-term score (1h) for scalp/day trading
    - asi_medium: Medium-term score (4h + 1d) for swing trading
    - asi_long: Long-term score (1d + 1w) for position/HODL
    - asi_combined: Technical (60%) + OnChain (40%)
    """
    import asyncio
    from app.core.config import get_settings
    
    settings = get_settings()
    analyzer = AnalyzerService(db, settings)
    
    # Default fallback data
    default_data = {
        "coin_id": coin_id,
        "asi_short": 50,
        "asi_medium": 50,
        "asi_long": 50,
        "asi_combined": 50,
        "signal_short": "NEUTRAL",
        "signal_medium": "NEUTRAL",
        "signal_long": "NEUTRAL",
        "signal_combined": "NEUTRAL",
    }
    
    try:
        # Add 25-second timeout to prevent gateway timeout (504)
        result = await asyncio.wait_for(
            analyzer.calculate_multi_horizon_asi(coin_id),
            timeout=25.0
        )
        return {
            "success": True,
            "data": result,
        }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Calculation timed out - using default values",
            "data": default_data,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": default_data,
        }
