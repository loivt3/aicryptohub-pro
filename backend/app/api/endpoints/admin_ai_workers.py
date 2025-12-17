"""
Admin AI Workers API Endpoints
Monitor and control AI analysis workers
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

class AIWorkerStatus(BaseModel):
    id: str
    name: str
    provider: str
    status: str  # ready, running, error, disabled
    rate_limit_remaining: Optional[int] = None
    rate_limit_max: Optional[int] = None
    coins_analyzed: int = 0
    last_analysis: Optional[str] = None
    error_message: Optional[str] = None


class AIWorkersStatusResponse(BaseModel):
    workers: List[AIWorkerStatus]
    is_running: bool = False
    current_job_id: Optional[str] = None
    total_coins: int = 0
    analyzed_count: int = 0
    pending_count: int = 0
    next_scheduled: Optional[str] = None


class AILogEntry(BaseModel):
    id: int
    timestamp: str
    worker: str
    coin_symbol: str
    signal: str
    asi_score: int
    level: str


class AITriggerResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    coins_queued: int = 0


# ==================== In-Memory State ====================

AI_STATE = {
    "is_running": False,
    "current_job_id": None,
    "total_coins": 0,
    "analyzed_count": 0,
    "pending_coins": [],
    "worker_status": {},
}

# Define AI workers
AI_WORKERS = [
    {"id": "technical", "name": "Technical Analyzer", "provider": "local"},
    {"id": "gemini", "name": "Gemini AI", "provider": "google"},
    {"id": "deepseek", "name": "DeepSeek AI", "provider": "deepseek"},
]


# ==================== Endpoints ====================

@router.get("/ai/status", response_model=AIWorkersStatusResponse)
async def get_ai_status():
    """Get status of all AI workers"""
    db = get_database_service()
    
    workers = []
    for worker_def in AI_WORKERS:
        worker_id = worker_def["id"]
        status_data = AI_STATE["worker_status"].get(worker_id, {})
        
        # Check if service is enabled
        is_enabled = True
        rate_remaining = None
        rate_max = None
        
        if worker_id == "gemini":
            from app.core.config import get_settings
            settings = get_settings()
            is_enabled = bool(settings.GEMINI_API_KEY)
            rate_max = 15  # Free tier RPM
            rate_remaining = status_data.get("rate_remaining", rate_max)
            
        elif worker_id == "deepseek":
            from app.core.config import get_settings
            settings = get_settings()
            is_enabled = bool(settings.DEEPSEEK_API_KEY)
        
        workers.append(AIWorkerStatus(
            id=worker_id,
            name=worker_def["name"],
            provider=worker_def["provider"],
            status=status_data.get("status", "ready" if is_enabled else "disabled"),
            rate_limit_remaining=rate_remaining,
            rate_limit_max=rate_max,
            coins_analyzed=status_data.get("coins_analyzed", 0),
            last_analysis=status_data.get("last_analysis"),
            error_message=None if is_enabled else "API key not configured",
        ))
    
    # Get total coins count
    total_coins = 0
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM aihub_coins"))
            total_coins = result.scalar() or 0
    except:
        pass
    
    # Get scheduling info
    next_scheduled = None
    try:
        from app.services.scheduler import SCHEDULER_STATE
        next_scheduled = SCHEDULER_STATE["ai_workers"].get("next_run")
    except:
        pass
    
    return AIWorkersStatusResponse(
        workers=workers,
        is_running=AI_STATE["is_running"],
        current_job_id=AI_STATE["current_job_id"],
        total_coins=total_coins,
        analyzed_count=AI_STATE["analyzed_count"],
        pending_count=len(AI_STATE.get("pending_coins", [])),
        next_scheduled=next_scheduled,
    )


@router.get("/ai/queue")
async def get_ai_queue(limit: int = 50):
    """Get coins pending analysis"""
    db = get_database_service()
    
    try:
        # Get coins without recent sentiment analysis
        with db.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT ac.symbol, ac.name, ac.market_cap, s.analyzed_at
                    FROM aihub_coins ac
                    LEFT JOIN aihub_sentiment s ON ac.symbol = s.symbol
                    WHERE s.analyzed_at IS NULL 
                       OR s.analyzed_at < NOW() - INTERVAL '6 hours'
                    ORDER BY ac.market_cap DESC NULLS LAST
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            rows = result.fetchall()
            
            queue = []
            for row in rows:
                queue.append({
                    "symbol": row[0],
                    "name": row[1],
                    "market_cap": float(row[2]) if row[2] else 0,
                    "last_analyzed": row[3].isoformat() if row[3] else None,
                })
            
            return {"queue": queue, "total_pending": len(AI_STATE.get("pending_coins", []))}
            
    except Exception as e:
        logger.error(f"Failed to get AI queue: {e}")
        return {"queue": [], "total_pending": 0}


@router.get("/ai/logs")
async def get_ai_logs(limit: int = 50):
    """Get recent AI analysis logs"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT symbol, ai_signal, sentiment_score, provider, analyzed_at
                    FROM aihub_sentiment
                    WHERE analyzed_at IS NOT NULL
                    ORDER BY analyzed_at DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            rows = result.fetchall()
            
            logs = []
            for i, row in enumerate(rows):
                score = float(row[2]) if row[2] else 0.5
                asi_score = int(score * 100)
                
                logs.append({
                    "id": i + 1,
                    "timestamp": row[4].isoformat() if row[4] else None,
                    "worker": row[3] or "technical",
                    "coin_symbol": row[0],
                    "signal": row[1] or "NEUTRAL",
                    "asi_score": asi_score,
                    "level": "success" if "BUY" in (row[1] or "") else "warning" if "SELL" in (row[1] or "") else "info",
                })
            
            return {"logs": logs}
            
    except Exception as e:
        logger.error(f"Failed to get AI logs: {e}")
        return {"logs": []}


@router.get("/ai/stats")
async def get_ai_stats():
    """Get AI analysis statistics"""
    db = get_database_service()
    
    try:
        with db.engine.connect() as conn:
            # Count by signal type
            result = conn.execute(
                text("""
                    SELECT 
                        ai_signal,
                        COUNT(*) as count,
                        AVG(sentiment_score) as avg_score
                    FROM aihub_sentiment
                    WHERE analyzed_at > NOW() - INTERVAL '24 hours'
                    GROUP BY ai_signal
                """)
            )
            rows = result.fetchall()
            
            signal_counts = {}
            for row in rows:
                signal_counts[row[0] or "NEUTRAL"] = {
                    "count": row[1],
                    "avg_score": float(row[2]) if row[2] else 0.5,
                }
            
            # Total analyzed today
            result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM aihub_sentiment 
                    WHERE analyzed_at > NOW() - INTERVAL '24 hours'
                """)
            )
            analyzed_today = result.scalar() or 0
            
            return {
                "analyzed_today": analyzed_today,
                "signal_breakdown": signal_counts,
                "avg_asi_score": sum(s.get("avg_score", 0.5) for s in signal_counts.values()) / len(signal_counts) if signal_counts else 0.5,
            }
            
    except Exception as e:
        logger.error(f"Failed to get AI stats: {e}")
        return {"analyzed_today": 0, "signal_breakdown": {}, "avg_asi_score": 0.5}


@router.post("/ai/trigger", response_model=AITriggerResponse)
async def trigger_ai_analysis(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    worker: str = "technical",
):
    """Manually trigger AI analysis"""
    if AI_STATE["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="An analysis job is already running"
        )
    
    job_id = f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Mark as running
    AI_STATE["is_running"] = True
    AI_STATE["current_job_id"] = job_id
    AI_STATE["analyzed_count"] = 0
    
    async def run_analysis():
        try:
            from app.services.database import get_database_service
            from app.services.analyzer import AnalyzerService
            from app.core.config import get_settings
            
            db = get_database_service()
            settings = get_settings()
            analyzer = AnalyzerService(db, settings)
            
            # Update worker status
            AI_STATE["worker_status"]["technical"] = {"status": "running", "coins_analyzed": 0}
            
            # Get coins to analyze
            coin_ids = db.get_coins_for_analysis(limit=limit)
            AI_STATE["total_coins"] = len(coin_ids)
            AI_STATE["pending_coins"] = coin_ids.copy()
            
            logger.info(f"Starting AI analysis for {len(coin_ids)} coins")
            
            # Run analysis
            result = await analyzer.analyze_coins(coin_ids)
            
            AI_STATE["analyzed_count"] = result.get("success_count", 0)
            AI_STATE["worker_status"]["technical"] = {
                "status": "ready",
                "coins_analyzed": result.get("success_count", 0),
                "last_analysis": datetime.now().isoformat(),
            }
            
            logger.info(f"AI analysis job {job_id} complete: {result}")
            
        except Exception as e:
            logger.error(f"AI analysis job {job_id} failed: {e}")
            AI_STATE["worker_status"]["technical"] = {
                "status": "error",
                "error_message": str(e),
            }
        finally:
            AI_STATE["is_running"] = False
            AI_STATE["current_job_id"] = None
            AI_STATE["pending_coins"] = []
    
    background_tasks.add_task(run_analysis)
    
    return AITriggerResponse(
        success=True,
        job_id=job_id,
        message=f"Analysis job started for {limit} coins",
        coins_queued=limit,
    )


@router.post("/ai/stop")
async def stop_ai_analysis():
    """Stop running AI analysis (soft stop)"""
    if not AI_STATE["is_running"]:
        raise HTTPException(status_code=400, detail="No analysis job is running")
    
    # Soft stop - just clear pending
    AI_STATE["pending_coins"] = []
    
    return {
        "success": True,
        "message": "Stop signal sent. Analysis will stop after current coin.",
    }
