"""
Admin Fetcher API Endpoints
Monitor and control data fetching from all sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import text

from app.services.database import get_database_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== Models ====================

class SourceStatus(BaseModel):
    id: str
    name: str
    type: str  # aggregator, cex, dex
    status: str  # ready, running, error, disabled
    last_fetch: Optional[str] = None
    items_fetched: int = 0
    duration_ms: int = 0
    error_message: Optional[str] = None


class FetcherStatusResponse(BaseModel):
    sources: List[SourceStatus]
    last_full_fetch: Optional[str] = None
    next_scheduled: Optional[str] = None
    is_running: bool = False


class FetchLogEntry(BaseModel):
    id: int
    timestamp: str
    source: str
    level: str  # info, warning, error
    message: str
    items_count: int = 0
    duration_ms: int = 0


class FetchTriggerResponse(BaseModel):
    success: bool
    job_id: str
    message: str


# ==================== In-Memory State ====================
# Track current fetch status (will be replaced by Redis in production)

FETCH_STATE = {
    "is_running": False,
    "current_job_id": None,
    "last_fetch_time": None,
    "source_status": {},
}

# Define all data sources
DATA_SOURCES = [
    {"id": "coingecko", "name": "CoinGecko", "type": "aggregator"},
    {"id": "coincap", "name": "CoinCap", "type": "aggregator"},
    {"id": "binance", "name": "Binance", "type": "cex"},
    {"id": "okx", "name": "OKX", "type": "cex"},
    {"id": "bybit", "name": "Bybit", "type": "cex"},
    {"id": "kucoin", "name": "KuCoin", "type": "cex"},
    {"id": "gate", "name": "Gate.io", "type": "cex"},
    {"id": "geckoterminal", "name": "GeckoTerminal", "type": "dex"},
    {"id": "defillama", "name": "DeFiLlama", "type": "defi"},
    {"id": "cmc", "name": "CoinMarketCap", "type": "aggregator"},
]


# ==================== Endpoints ====================

@router.get("/fetcher/status", response_model=FetcherStatusResponse)
async def get_fetcher_status():
    """Get status of all data sources"""
    db = get_database_service()
    
    sources = []
    for source_def in DATA_SOURCES:
        source_id = source_def["id"]
        
        # Get status from memory or set default
        status_data = FETCH_STATE["source_status"].get(source_id, {})
        
        sources.append(SourceStatus(
            id=source_id,
            name=source_def["name"],
            type=source_def["type"],
            status=status_data.get("status", "ready"),
            last_fetch=status_data.get("last_fetch"),
            items_fetched=status_data.get("items_fetched", 0),
            duration_ms=status_data.get("duration_ms", 0),
            error_message=status_data.get("error_message"),
        ))
    
    # Get last fetch info from database
    last_fetch_time = FETCH_STATE.get("last_fetch_time")
    
    return FetcherStatusResponse(
        sources=sources,
        last_full_fetch=last_fetch_time.isoformat() if last_fetch_time else None,
        next_scheduled=None,  # TODO: Get from scheduler
        is_running=FETCH_STATE["is_running"],
    )


@router.get("/fetcher/logs")
async def get_fetcher_logs(limit: int = 50):
    """Get recent fetch logs from database"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            # Try to get logs from admin_api_logs filtered by fetch endpoints
            result = conn.execute(
                text("""
                    SELECT id, created_at, endpoint, status_code, duration_ms, error_message
                    FROM admin_api_logs 
                    WHERE endpoint LIKE '%/trigger%' OR endpoint LIKE '%/fetch%'
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            rows = result.fetchall()
            
            logs = []
            for row in rows:
                # Determine source from endpoint
                endpoint = row[2] or ""
                source = "system"
                if "fetch" in endpoint:
                    source = "multi-source"
                elif "ohlcv" in endpoint:
                    source = "binance"
                
                logs.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "source": source,
                    "level": "error" if row[3] >= 400 else "info",
                    "message": row[5] or f"Endpoint: {endpoint}",
                    "items_count": 0,
                    "duration_ms": row[4] or 0,
                })
            
            return {"logs": logs}
            
    except Exception as e:
        logger.error(f"Failed to get fetch logs: {e}")
        # Return mock logs if table doesn't exist
        return {
            "logs": [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "source": "system",
                    "level": "info",
                    "message": "Fetcher logs will appear here after fetch jobs run",
                    "items_count": 0,
                    "duration_ms": 0,
                }
            ]
        }


@router.post("/fetcher/trigger", response_model=FetchTriggerResponse)
async def trigger_fetch(background_tasks: BackgroundTasks, sources: List[str] = None):
    """Manually trigger data fetch"""
    if FETCH_STATE["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="A fetch job is already running"
        )
    
    job_id = f"fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Mark as running
    FETCH_STATE["is_running"] = True
    FETCH_STATE["current_job_id"] = job_id
    
    async def run_fetch():
        try:
            from app.services.data_fetcher import get_data_fetcher
            
            fetcher = get_data_fetcher()
            
            # Update source statuses to "running"
            for source in DATA_SOURCES:
                FETCH_STATE["source_status"][source["id"]] = {
                    "status": "running",
                    "last_fetch": None,
                    "items_fetched": 0,
                    "duration_ms": 0,
                }
            
            # Run the actual fetch
            start = datetime.now()
            result = await fetcher.fetch_and_save_coins()
            duration = (datetime.now() - start).total_seconds()
            
            # Update statuses
            FETCH_STATE["last_fetch_time"] = datetime.now()
            
            # Mark sources as complete (simplified - in real case, each source reports its status)
            for source in DATA_SOURCES:
                FETCH_STATE["source_status"][source["id"]] = {
                    "status": "ready",
                    "last_fetch": datetime.now().isoformat(),
                    "items_fetched": result.get("fetched", 0) // len(DATA_SOURCES),
                    "duration_ms": int(duration * 1000 / len(DATA_SOURCES)),
                }
            
            logger.info(f"Fetch job {job_id} complete: {result}")
            
        except Exception as e:
            logger.error(f"Fetch job {job_id} failed: {e}")
            # Mark sources as error
            for source in DATA_SOURCES:
                if FETCH_STATE["source_status"].get(source["id"], {}).get("status") == "running":
                    FETCH_STATE["source_status"][source["id"]] = {
                        "status": "error",
                        "error_message": str(e),
                    }
        finally:
            FETCH_STATE["is_running"] = False
            FETCH_STATE["current_job_id"] = None
    
    background_tasks.add_task(run_fetch)
    
    return FetchTriggerResponse(
        success=True,
        job_id=job_id,
        message=f"Fetch job started for {len(sources) if sources else 'all'} sources",
    )


@router.get("/fetcher/history")
async def get_fetcher_history(days: int = 7):
    """Get fetch history statistics"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            # Get daily fetch counts from api_logs
            result = conn.execute(
                text("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as fetch_count,
                        AVG(duration_ms) as avg_duration,
                        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                    FROM admin_api_logs 
                    WHERE endpoint LIKE '%/trigger/fetch%'
                      AND created_at >= NOW() - INTERVAL ':days days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """),
                {"days": days}
            )
            rows = result.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "date": row[0].isoformat() if row[0] else None,
                    "fetch_count": row[1],
                    "avg_duration_ms": round(row[2]) if row[2] else 0,
                    "error_count": row[3],
                })
            
            return {"history": history, "days": days}
            
    except Exception as e:
        logger.error(f"Failed to get fetch history: {e}")
        return {"history": [], "days": days}


@router.post("/fetcher/source/{source_id}/toggle")
async def toggle_source(source_id: str, enabled: bool = True):
    """Enable or disable a specific data source"""
    # Find source
    source = next((s for s in DATA_SOURCES if s["id"] == source_id), None)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")
    
    # Update status
    current_status = FETCH_STATE["source_status"].get(source_id, {})
    current_status["status"] = "ready" if enabled else "disabled"
    FETCH_STATE["source_status"][source_id] = current_status
    
    return {
        "success": True,
        "source_id": source_id,
        "enabled": enabled,
    }
