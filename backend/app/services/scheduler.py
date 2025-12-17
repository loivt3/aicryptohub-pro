"""
Background Scheduler Service
Runs periodic jobs for data fetching and AI analysis
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


# ==================== Global State ====================

SCHEDULER_STATE = {
    "fetcher": {
        "enabled": True,
        "interval_minutes": 3,
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    "ai_workers": {
        "enabled": True,
        "interval_minutes": 30,
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
}

_scheduler: Optional[AsyncIOScheduler] = None


# ==================== Job Functions ====================

async def run_fetcher_job():
    """Background job to fetch data from all sources"""
    if SCHEDULER_STATE["fetcher"]["is_running"]:
        logger.warning("Fetcher job already running, skipping")
        return
    
    SCHEDULER_STATE["fetcher"]["is_running"] = True
    SCHEDULER_STATE["fetcher"]["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.data_fetcher import get_data_fetcher
        from app.api.endpoints.admin_fetcher import FETCH_STATE, DATA_SOURCES
        
        logger.info("Scheduler: Starting fetcher job...")
        
        # Update fetcher state
        FETCH_STATE["is_running"] = True
        for source in DATA_SOURCES:
            FETCH_STATE["source_status"][source["id"]] = {"status": "running"}
        
        fetcher = get_data_fetcher()
        result = await fetcher.fetch_and_save_coins()
        
        # Update states
        SCHEDULER_STATE["fetcher"]["last_result"] = result
        FETCH_STATE["last_fetch_time"] = datetime.now()
        
        for source in DATA_SOURCES:
            FETCH_STATE["source_status"][source["id"]] = {
                "status": "ready",
                "last_fetch": datetime.now().isoformat(),
            }
        
        logger.info(f"Scheduler: Fetcher job complete - {result}")
        
    except Exception as e:
        logger.error(f"Scheduler: Fetcher job failed - {e}")
        SCHEDULER_STATE["fetcher"]["last_result"] = {"error": str(e)}
    finally:
        SCHEDULER_STATE["fetcher"]["is_running"] = False
        from app.api.endpoints.admin_fetcher import FETCH_STATE
        FETCH_STATE["is_running"] = False


async def run_ai_workers_job():
    """Background job to run AI analysis"""
    if SCHEDULER_STATE["ai_workers"]["is_running"]:
        logger.warning("AI Workers job already running, skipping")
        return
    
    SCHEDULER_STATE["ai_workers"]["is_running"] = True
    SCHEDULER_STATE["ai_workers"]["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.database import get_database_service
        from app.services.analyzer import AnalyzerService
        from app.core.config import get_settings
        from app.api.endpoints.admin_ai_workers import AI_STATE
        
        logger.info("Scheduler: Starting AI Workers job...")
        
        db = get_database_service()
        settings = get_settings()
        analyzer = AnalyzerService(db, settings)
        
        # Update AI state
        AI_STATE["is_running"] = True
        AI_STATE["worker_status"]["technical"] = {"status": "running"}
        
        # Get coins and analyze
        coin_ids = db.get_coins_for_analysis(limit=100)
        AI_STATE["total_coins"] = len(coin_ids)
        
        result = await analyzer.analyze_coins(coin_ids)
        
        # Update states
        SCHEDULER_STATE["ai_workers"]["last_result"] = result
        AI_STATE["analyzed_count"] = result.get("success_count", 0)
        AI_STATE["worker_status"]["technical"] = {
            "status": "ready",
            "coins_analyzed": result.get("success_count", 0),
            "last_analysis": datetime.now().isoformat(),
        }
        
        logger.info(f"Scheduler: AI Workers job complete - {result}")
        
    except Exception as e:
        logger.error(f"Scheduler: AI Workers job failed - {e}")
        SCHEDULER_STATE["ai_workers"]["last_result"] = {"error": str(e)}
    finally:
        SCHEDULER_STATE["ai_workers"]["is_running"] = False
        from app.api.endpoints.admin_ai_workers import AI_STATE
        AI_STATE["is_running"] = False


# ==================== Scheduler Management ====================

def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance"""
    return _scheduler


def start_scheduler():
    """Initialize and start the background scheduler"""
    global _scheduler
    
    if _scheduler is not None:
        logger.warning("Scheduler already started")
        return
    
    _scheduler = AsyncIOScheduler()
    
    # Add Fetcher job - every 3 minutes
    if SCHEDULER_STATE["fetcher"]["enabled"]:
        _scheduler.add_job(
            run_fetcher_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["fetcher"]["interval_minutes"]),
            id="fetcher_job",
            name="Data Fetcher",
            replace_existing=True,
        )
        logger.info(f"Scheduled Fetcher job: every {SCHEDULER_STATE['fetcher']['interval_minutes']} minutes")
    
    # Add AI Workers job - every 30 minutes
    if SCHEDULER_STATE["ai_workers"]["enabled"]:
        _scheduler.add_job(
            run_ai_workers_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ai_workers"]["interval_minutes"]),
            id="ai_workers_job",
            name="AI Workers",
            replace_existing=True,
        )
        logger.info(f"Scheduled AI Workers job: every {SCHEDULER_STATE['ai_workers']['interval_minutes']} minutes")
    
    _scheduler.start()
    logger.info("Background scheduler started")
    
    # Update next run times
    for job in _scheduler.get_jobs():
        if job.id == "fetcher_job":
            SCHEDULER_STATE["fetcher"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
        elif job.id == "ai_workers_job":
            SCHEDULER_STATE["ai_workers"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None


def stop_scheduler():
    """Stop the background scheduler"""
    global _scheduler
    
    if _scheduler is None:
        return
    
    _scheduler.shutdown(wait=False)
    _scheduler = None
    logger.info("Background scheduler stopped")


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status"""
    # Update next run times
    if _scheduler:
        for job in _scheduler.get_jobs():
            if job.id == "fetcher_job":
                SCHEDULER_STATE["fetcher"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
            elif job.id == "ai_workers_job":
                SCHEDULER_STATE["ai_workers"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
    
    return {
        "scheduler_running": _scheduler is not None and _scheduler.running,
        "jobs": SCHEDULER_STATE,
    }


def toggle_job(job_name: str, enabled: bool) -> bool:
    """Enable or disable a scheduled job"""
    if job_name not in SCHEDULER_STATE:
        return False
    
    SCHEDULER_STATE[job_name]["enabled"] = enabled
    
    if _scheduler:
        job_id = f"{job_name}_job"
        if enabled:
            # Re-add job
            if job_name == "fetcher":
                _scheduler.add_job(
                    run_fetcher_job,
                    trigger=IntervalTrigger(minutes=SCHEDULER_STATE["fetcher"]["interval_minutes"]),
                    id=job_id,
                    replace_existing=True,
                )
            elif job_name == "ai_workers":
                _scheduler.add_job(
                    run_ai_workers_job,
                    trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ai_workers"]["interval_minutes"]),
                    id=job_id,
                    replace_existing=True,
                )
            logger.info(f"Job {job_name} enabled")
        else:
            try:
                _scheduler.remove_job(job_id)
                logger.info(f"Job {job_name} disabled")
            except:
                pass
    
    return True
