"""
Market Discovery API Endpoints
Fast access to pre-computed market metrics.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, Depends, BackgroundTasks

from app.services.database import DatabaseService, get_db_service
from app.services.discovery_engine import DiscoveryEngine, get_discovery_engine

router = APIRouter()


@router.get("/top-gainers")
async def get_top_gainers(
    timeframe: str = Query(default="1h", description="1h, 4h, 24h, or 7d"),
    limit: int = Query(default=10, le=50),
):
    """
    Get top gaining coins.
    
    Args:
        timeframe: Time period for % change (1h, 4h, 24h, 7d)
        limit: Number of results (max 50)
        
    Returns:
        List of top gainers sorted by % change DESC
    """
    engine = get_discovery_engine()
    data = engine.get_top_gainers(timeframe=timeframe, limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "timeframe": timeframe,
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/top-losers")
async def get_top_losers(
    timeframe: str = Query(default="1h", description="1h, 4h, 24h, or 7d"),
    limit: int = Query(default=10, le=50),
):
    """
    Get top losing coins.
    
    Args:
        timeframe: Time period for % change (1h, 4h, 24h, 7d)
        limit: Number of results (max 50)
        
    Returns:
        List of top losers sorted by % change ASC
    """
    engine = get_discovery_engine()
    data = engine.get_top_losers(timeframe=timeframe, limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "timeframe": timeframe,
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/sudden-pump")
async def get_sudden_pumps(
    limit: int = Query(default=10, le=50),
):
    """
    Get coins with sudden pump signals.
    
    Criteria:
    - change_1h > 3%
    - volume_1h > 2x average hourly volume
    - volume_24h > $100k (filter low liquidity)
    
    Returns:
        List of sudden pump candidates
    """
    engine = get_discovery_engine()
    data = engine.get_sudden_pumps(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "detection_criteria": {
                "min_change_1h": "3%",
                "min_volume_spike": "2x average",
                "min_volume_24h": "$100k",
            },
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/sudden-dump")
async def get_sudden_dumps(
    limit: int = Query(default=10, le=50),
):
    """
    Get coins with sudden dump/crash signals.
    
    Criteria:
    - change_1h < -3%
    - volume_1h > 2x average hourly volume
    - volume_24h > $100k (filter low liquidity)
    
    Returns:
        List of sudden dump candidates
    """
    engine = get_discovery_engine()
    data = engine.get_sudden_dumps(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "detection_criteria": {
                "max_change_1h": "-3%",
                "min_volume_spike": "2x average",
                "min_volume_24h": "$100k",
            },
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/most-traded")
async def get_most_traded(
    limit: int = Query(default=10, le=50),
):
    """
    Get most traded coins by 24h volume.
    
    Returns:
        List of most traded coins sorted by volume DESC
    """
    engine = get_discovery_engine()
    data = engine.get_most_traded(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.post("/refresh")
async def refresh_discovery_snapshot(
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Trigger a refresh of the discovery snapshot.
    
    Note: This is usually handled by the scheduler (every 5 min).
    Use this endpoint for manual refresh.
    """
    engine = DiscoveryEngine(db)
    
    async def run_update():
        await engine.update_snapshot()
    
    background_tasks.add_task(run_update)
    
    return {
        "success": True,
        "message": "Discovery snapshot refresh scheduled",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/status")
async def get_discovery_status():
    """Get current discovery snapshot status."""
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        with db.engine.connect() as conn:
            # Get snapshot stats
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_coins,
                    COUNT(CASE WHEN is_sudden_pump THEN 1 END) as pumps,
                    COUNT(CASE WHEN is_sudden_dump THEN 1 END) as dumps,
                    MAX(updated_at) as last_update
                FROM market_discovery_snapshot
            """))
            row = result.fetchone()
            
            if row:
                return {
                    "success": True,
                    "data": {
                        "total_coins": row[0],
                        "active_pumps": row[1],
                        "active_dumps": row[2],
                        "last_update": row[3].isoformat() if row[3] else None,
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No snapshot data found",
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
