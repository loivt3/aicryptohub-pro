"""
AI Risk Assessment API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from app.services.ai_risk import ai_risk_service
from app.services.database import get_db_service, DatabaseService

router = APIRouter()


@router.get("/{coin_id}")
async def get_coin_risk(
    coin_id: str,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Get risk assessment for a specific coin.
    
    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
        
    Returns:
        Risk assessment with score, level, and factors breakdown
    """
    # Get coin data from database
    coin = db.get_coin_by_id(coin_id)
    
    if not coin:
        raise HTTPException(status_code=404, detail=f"Coin {coin_id} not found")
    
    # Calculate risk
    risk = ai_risk_service.calculate_risk_score(coin)
    
    return risk


@router.get("/top/risky")
async def get_top_risky_coins(
    limit: int = 10,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Get top riskiest coins in the market.
    
    Args:
        limit: Number of coins to return (default 10)
        
    Returns:
        List of coins sorted by risk score descending
    """
    # Get market data
    coins = db.get_market_data(limit=200)
    
    if not coins:
        return []
    
    # Get top risky
    top_risks = ai_risk_service.get_top_risky_coins(coins, limit=limit)
    
    return top_risks


@router.get("/overview/market")
async def get_market_risk_overview(
    db: DatabaseService = Depends(get_db_service),
):
    """
    Get overall market risk summary.
    
    Returns:
        Market-wide risk metrics including average score and distribution
    """
    # Get market data
    coins = db.get_market_data(limit=100)
    
    if not coins:
        return {
            "average_risk": 50,
            "risk_level": "MED_RISK",
            "distribution": {},
            "top_risks": [],
        }
    
    # Calculate overview
    overview = ai_risk_service.get_market_risk_overview(coins)
    
    return overview


@router.get("/batch")
async def get_batch_risk(
    coin_ids: str,  # Comma-separated
    db: DatabaseService = Depends(get_db_service),
):
    """
    Get risk assessment for multiple coins.
    
    Args:
        coin_ids: Comma-separated list of coin IDs
        
    Returns:
        List of risk assessments
    """
    ids = [c.strip() for c in coin_ids.split(",") if c.strip()]
    
    if not ids:
        return []
    
    results = []
    for coin_id in ids[:20]:  # Limit to 20
        coin = db.get_coin_by_id(coin_id)
        if coin:
            risk = ai_risk_service.calculate_risk_score(coin)
            results.append(risk)
    
    return results
