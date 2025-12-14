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
