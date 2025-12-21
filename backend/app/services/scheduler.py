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
    "onchain_collector": {
        "enabled": True,
        "interval_minutes": 30,
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    # Multi-TF OHLCV jobs (timeframes: 1h, 4h, 1d, 1w, 1M)
    "ohlcv_4h": {
        "enabled": True,
        "interval_minutes": 240,  # 4 hours
        "timeframe": "4h",
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    "ohlcv_1d": {
        "enabled": True,
        "interval_minutes": 1440,  # 24 hours
        "timeframe": "1d",
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    "ohlcv_1w": {
        "enabled": True,
        "interval_minutes": 10080,  # 7 days
        "timeframe": "1w",
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    "ohlcv_1M": {
        "enabled": True,
        "interval_minutes": 43200,  # 30 days (1 month)
        "timeframe": "1M",
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    # Multi-Horizon ASI Pre-compute Job - Tier 1 (Top 50, frequent)
    "multi_horizon": {
        "enabled": True,
        "interval_minutes": 5,  # Every 5 minutes
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    # Multi-Horizon ASI Pre-compute Job - Tier 2 (Coins 51-200, less frequent)
    "multi_horizon_tier2": {
        "enabled": True,
        "interval_minutes": 15,  # Every 15 minutes
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
        from app.api.endpoints.admin_fetcher import FETCH_STATE, DATA_SOURCES, add_fetch_log
        
        logger.info("Scheduler: Starting fetcher job...")
        add_fetch_log("scheduler", "info", "Starting scheduled fetch job")
        
        # Update fetcher state
        FETCH_STATE["is_running"] = True
        for source in DATA_SOURCES:
            FETCH_STATE["source_status"][source["id"]] = {"status": "running"}
        
        start_time = datetime.now()
        fetcher = get_data_fetcher()
        result = await fetcher.fetch_and_save_coins()
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Update states
        SCHEDULER_STATE["fetcher"]["last_result"] = result
        FETCH_STATE["last_fetch_time"] = datetime.now()
        
        items_count = result.get("fetched", 0) if isinstance(result, dict) else 0
        
        for source in DATA_SOURCES:
            FETCH_STATE["source_status"][source["id"]] = {
                "status": "ready",
                "last_fetch": datetime.now().isoformat(),
                "items_fetched": items_count // len(DATA_SOURCES),
                "duration_ms": duration_ms // len(DATA_SOURCES),
            }
        
        # Add success log
        add_fetch_log(
            "multi-source", "info", 
            f"Fetch complete: {items_count} items from {len(DATA_SOURCES)} sources",
            items_count=items_count,
            duration_ms=duration_ms
        )
        
        logger.info(f"Scheduler: Fetcher job complete - {result}")
        
    except Exception as e:
        logger.error(f"Scheduler: Fetcher job failed - {e}")
        SCHEDULER_STATE["fetcher"]["last_result"] = {"error": str(e)}
        
        # Add error log
        try:
            from app.api.endpoints.admin_fetcher import add_fetch_log
            add_fetch_log("scheduler", "error", f"Fetch failed: {str(e)}")
        except:
            pass
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


async def run_onchain_job():
    """Background job to collect on-chain whale transactions"""
    if SCHEDULER_STATE["onchain_collector"]["is_running"]:
        logger.warning("On-chain collector job already running, skipping")
        return
    
    SCHEDULER_STATE["onchain_collector"]["is_running"] = True
    SCHEDULER_STATE["onchain_collector"]["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.database import get_database_service
        from app.services.onchain_collector import OnChainCollector
        from app.core.config import get_settings
        
        logger.info("Scheduler: Starting On-chain collector job...")
        
        db = get_database_service()
        settings = get_settings()
        
        # Initialize collector with Etherscan API key
        collector = OnChainCollector(db, settings.ETHERSCAN_API_KEY)
        
        # Load exchange addresses for whale classification
        await collector.load_exchange_addresses()
        
        # Get top coins with contract addresses
        coins = db.get_coins_with_contracts(limit=20)
        
        stats = {
            "whale_txs_found": 0,
            "coins_processed": 0,
            "errors": 0,
        }
        
        for coin in coins:
            try:
                coin_id = coin.get("coin_id")
                contract = coin.get("contract_address")
                chain_id = coin.get("chain_id", 1)
                price = coin.get("price", 0)
                
                if not contract or not price:
                    continue
                
                # Collect whale transactions
                whale_txs = await collector.collect_whale_transactions(
                    coin_id=coin_id,
                    chain_slug=coin.get("chain_slug", "ethereum"),
                    chain_id=chain_id,
                    contract_address=contract,
                    token_price_usd=price,
                    token_decimals=coin.get("decimals", 18),
                    hours_back=24,
                )
                
                if whale_txs:
                    # Save whale transactions and update signals
                    await collector.save_whale_transactions(whale_txs)
                    await collector.update_onchain_signals(coin_id, whale_txs)
                    stats["whale_txs_found"] += len(whale_txs)
                
                stats["coins_processed"] += 1
                
            except Exception as e:
                logger.warning(f"Failed to collect on-chain for {coin.get('coin_id')}: {e}")
                stats["errors"] += 1
        
        SCHEDULER_STATE["onchain_collector"]["last_result"] = stats
        logger.info(f"Scheduler: On-chain job complete - {stats}")
        
    except Exception as e:
        logger.error(f"Scheduler: On-chain collector job failed - {e}")
        SCHEDULER_STATE["onchain_collector"]["last_result"] = {"error": str(e)}
    finally:
        SCHEDULER_STATE["onchain_collector"]["is_running"] = False


async def run_ohlcv_job(job_name: str, timeframe: str):
    """
    Background job to fetch OHLCV data for a specific timeframe.
    
    Args:
        job_name: State key like 'ohlcv_1m', 'ohlcv_4h', etc.
        timeframe: Timeframe string '1m', '4h', '1d', '1w'
    """
    if SCHEDULER_STATE[job_name]["is_running"]:
        logger.warning(f"OHLCV job [{timeframe}] already running, skipping")
        return
    
    SCHEDULER_STATE[job_name]["is_running"] = True
    SCHEDULER_STATE[job_name]["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.data_fetcher import get_data_fetcher
        
        logger.info(f"Scheduler: Starting OHLCV job [{timeframe}]...")
        
        fetcher = get_data_fetcher()
        result = await fetcher.fetch_ohlcv_for_all_coins(timeframe=timeframe)
        
        SCHEDULER_STATE[job_name]["last_result"] = result
        logger.info(f"Scheduler: OHLCV [{timeframe}] job complete - {result}")
        
    except Exception as e:
        logger.error(f"Scheduler: OHLCV [{timeframe}] job failed - {e}")
        SCHEDULER_STATE[job_name]["last_result"] = {"error": str(e)}
    finally:
        SCHEDULER_STATE[job_name]["is_running"] = False


# Factory functions for APScheduler (can't pass args directly)
async def run_ohlcv_4h_job():
    await run_ohlcv_job("ohlcv_4h", "4h")

async def run_ohlcv_1d_job():
    await run_ohlcv_job("ohlcv_1d", "1d")

async def run_ohlcv_1w_job():
    await run_ohlcv_job("ohlcv_1w", "1w")

async def run_ohlcv_1M_job():
    await run_ohlcv_job("ohlcv_1M", "1M")


async def run_multi_horizon_job():
    """
    Pre-compute multi-horizon ASI for top 50 coins.
    This populates the cache so batch API calls are instant.
    """
    state = SCHEDULER_STATE["multi_horizon"]
    if state["is_running"]:
        logger.warning("Multi-horizon job already running, skipping")
        return
    
    state["is_running"] = True
    state["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.database import get_database_service
        from app.services.analyzer import AnalyzerService
        from app.core.config import get_settings
        
        logger.info("Scheduler: Starting Multi-Horizon pre-compute job...")
        
        db = get_database_service()
        settings = get_settings()
        
        # Ensure cache table exists
        db.ensure_multi_horizon_table()
        
        analyzer = AnalyzerService(db, settings)
        
        # Get top 50 coins by market cap
        coins = db.get_market_data(limit=50, orderby="market_cap")
        coin_ids = [c["coin_id"] for c in coins if c.get("coin_id")]
        
        computed = 0
        failed = 0
        
        for coin_id in coin_ids:
            try:
                # Force fresh calculation (skip cache)
                result = await asyncio.wait_for(
                    analyzer.calculate_multi_horizon_asi(coin_id, use_cache=False),
                    timeout=30.0
                )
                if result:
                    computed += 1
            except asyncio.TimeoutError:
                logger.warning(f"Multi-horizon timeout for {coin_id}")
                failed += 1
            except Exception as e:
                logger.warning(f"Multi-horizon failed for {coin_id}: {e}")
                failed += 1
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
        
        state["last_result"] = {
            "computed": computed,
            "failed": failed,
            "total": len(coin_ids),
        }
        
        logger.info(f"Scheduler: Multi-Horizon job complete - computed {computed}/{len(coin_ids)}, failed {failed}")
        
    except Exception as e:
        logger.error(f"Scheduler: Multi-Horizon job failed - {e}")
        state["last_result"] = {"error": str(e)}
    finally:
        state["is_running"] = False


async def run_multi_horizon_tier2_job():
    """
    Pre-compute multi-horizon ASI for coins ranked 51-200.
    Runs less frequently (every 15 min) for extended coverage.
    """
    state = SCHEDULER_STATE["multi_horizon_tier2"]
    if state["is_running"]:
        logger.warning("Multi-horizon tier2 job already running, skipping")
        return
    
    state["is_running"] = True
    state["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.database import get_database_service
        from app.services.analyzer import AnalyzerService
        from app.core.config import get_settings
        
        logger.info("Scheduler: Starting Multi-Horizon Tier 2 (coins 51-200) job...")
        
        db = get_database_service()
        settings = get_settings()
        
        # Ensure cache table exists
        db.ensure_multi_horizon_table()
        
        analyzer = AnalyzerService(db, settings)
        
        # Get coins 51-200 by market cap (skip first 50, take next 150)
        all_coins = db.get_market_data(limit=200, orderby="market_cap")
        tier2_coins = all_coins[50:]  # Skip top 50
        coin_ids = [c["coin_id"] for c in tier2_coins if c.get("coin_id")]
        
        computed = 0
        failed = 0
        
        for coin_id in coin_ids:
            try:
                # Force fresh calculation (skip cache)
                result = await asyncio.wait_for(
                    analyzer.calculate_multi_horizon_asi(coin_id, use_cache=False),
                    timeout=30.0
                )
                if result:
                    computed += 1
            except asyncio.TimeoutError:
                logger.warning(f"Multi-horizon tier2 timeout for {coin_id}")
                failed += 1
            except Exception as e:
                logger.debug(f"Multi-horizon tier2 failed for {coin_id}: {e}")
                failed += 1
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.15)
        
        state["last_result"] = {
            "computed": computed,
            "failed": failed,
            "total": len(coin_ids),
            "tier": "51-200",
        }
        
        logger.info(f"Scheduler: Multi-Horizon Tier 2 complete - computed {computed}/{len(coin_ids)}, failed {failed}")
        
    except Exception as e:
        logger.error(f"Scheduler: Multi-Horizon Tier 2 job failed - {e}")
        state["last_result"] = {"error": str(e)}
    finally:
        state["is_running"] = False


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
    
    # Add On-chain Collector job - every 30 minutes
    if SCHEDULER_STATE["onchain_collector"]["enabled"]:
        _scheduler.add_job(
            run_onchain_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["onchain_collector"]["interval_minutes"]),
            id="onchain_collector_job",
            name="On-chain Collector",
            replace_existing=True,
        )
        logger.info(f"Scheduled On-chain Collector job: every {SCHEDULER_STATE['onchain_collector']['interval_minutes']} minutes")
    
    # Add OHLCV 4h job - every 4 hours
    if SCHEDULER_STATE["ohlcv_4h"]["enabled"]:
        _scheduler.add_job(
            run_ohlcv_4h_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ohlcv_4h"]["interval_minutes"]),
            id="ohlcv_4h_job",
            name="OHLCV 4h Fetcher",
            replace_existing=True,
        )
        logger.info(f"Scheduled OHLCV 4h job: every {SCHEDULER_STATE['ohlcv_4h']['interval_minutes']} minutes")
    
    # Add OHLCV 1d job - every 24 hours
    if SCHEDULER_STATE["ohlcv_1d"]["enabled"]:
        _scheduler.add_job(
            run_ohlcv_1d_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ohlcv_1d"]["interval_minutes"]),
            id="ohlcv_1d_job",
            name="OHLCV 1d Fetcher",
            replace_existing=True,
        )
        logger.info(f"Scheduled OHLCV 1d job: every {SCHEDULER_STATE['ohlcv_1d']['interval_minutes']} minutes")
    
    # Add OHLCV 1w job - every 7 days
    if SCHEDULER_STATE["ohlcv_1w"]["enabled"]:
        _scheduler.add_job(
            run_ohlcv_1w_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ohlcv_1w"]["interval_minutes"]),
            id="ohlcv_1w_job",
            name="OHLCV 1w Fetcher",
            replace_existing=True,
        )
        logger.info(f"Scheduled OHLCV 1w job: every {SCHEDULER_STATE['ohlcv_1w']['interval_minutes']} minutes")
    
    # Add OHLCV 1M job - every 30 days (1 month)
    if SCHEDULER_STATE["ohlcv_1M"]["enabled"]:
        _scheduler.add_job(
            run_ohlcv_1M_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["ohlcv_1M"]["interval_minutes"]),
            id="ohlcv_1M_job",
            name="OHLCV 1M (Monthly) Fetcher",
            replace_existing=True,
        )
        logger.info(f"Scheduled OHLCV 1M (monthly) job: every {SCHEDULER_STATE['ohlcv_1M']['interval_minutes']} minutes")
    
    # Add Multi-Horizon pre-compute job - Tier 1: Top 50, every 5 minutes
    if SCHEDULER_STATE["multi_horizon"]["enabled"]:
        _scheduler.add_job(
            run_multi_horizon_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["multi_horizon"]["interval_minutes"]),
            id="multi_horizon_job",
            name="Multi-Horizon ASI Pre-compute (Top 50)",
            replace_existing=True,
        )
        logger.info(f"Scheduled Multi-Horizon Tier 1 job: every {SCHEDULER_STATE['multi_horizon']['interval_minutes']} minutes (Top 50)")
    
    # Add Multi-Horizon pre-compute job - Tier 2: Coins 51-200, every 15 minutes
    if SCHEDULER_STATE["multi_horizon_tier2"]["enabled"]:
        _scheduler.add_job(
            run_multi_horizon_tier2_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["multi_horizon_tier2"]["interval_minutes"]),
            id="multi_horizon_tier2_job",
            name="Multi-Horizon ASI Pre-compute (51-200)",
            replace_existing=True,
        )
        logger.info(f"Scheduled Multi-Horizon Tier 2 job: every {SCHEDULER_STATE['multi_horizon_tier2']['interval_minutes']} minutes (51-200)")
    
    _scheduler.start()
    logger.info("Background scheduler started")
    
    # Update next run times
    for job in _scheduler.get_jobs():
        if job.id == "fetcher_job":
            SCHEDULER_STATE["fetcher"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
        elif job.id == "ai_workers_job":
            SCHEDULER_STATE["ai_workers"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
        elif job.id == "onchain_collector_job":
            SCHEDULER_STATE["onchain_collector"]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
        elif job.id.startswith("ohlcv_"):
            # Update OHLCV job next run times
            job_key = job.id.replace("_job", "")
            if job_key in SCHEDULER_STATE:
                SCHEDULER_STATE[job_key]["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None


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
