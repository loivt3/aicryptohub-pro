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
        "interval_minutes": 10,
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
        "interval_minutes": 360,  # 6 hours (faster population, stable data)
        "timeframe": "1w",
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    "ohlcv_1M": {
        "enabled": True,
        "interval_minutes": 1440,  # 24 hours (faster population)
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
    # Market Discovery Engine - Top Gainers/Losers snapshot
    "discovery_engine": {
        "enabled": True,
        "interval_minutes": 2,  # Every 2 minutes for fresher data
        "last_run": None,
        "next_run": None,
        "is_running": False,
        "last_result": None,
    },
    # Hidden Gems Performance Tracker - evaluates gem success
    "gems_tracker": {
        "enabled": True,
        "interval_minutes": 360,  # Every 6 hours
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
            "dau_collected": 0,
            "holders_collected": 0,
            "coins_processed": 0,
            "signals_updated": 0,
            "errors": 0,
        }
        
        for coin in coins:
            try:
                coin_id = coin.get("coin_id")
                contract = coin.get("contract_address")
                chain_id = int(coin.get("chain_id", 1))  # Ensure integer
                chain_slug = coin.get("chain_slug", "ethereum")
                price = coin.get("price", 0)
                decimals = int(coin.get("decimals", 18))  # Ensure integer
                
                if not coin_id:
                    continue
                
                whale_txs = []
                
                # Collect whale transactions (requires contract and price)
                if contract and price > 0:
                    whale_txs = await collector.collect_whale_transactions(
                        coin_id=coin_id,
                        chain_slug=chain_slug,
                        chain_id=chain_id,
                        contract_address=contract,
                        token_price_usd=price,
                        token_decimals=decimals,
                        hours_back=24,
                    )
                    
                    if whale_txs:
                        await collector.save_whale_transactions(whale_txs)
                        stats["whale_txs_found"] += len(whale_txs)
                
                # Collect DAU (Daily Active Addresses)
                if contract:
                    try:
                        dau_data = await collector.collect_daily_active_addresses(
                            coin_id=coin_id,
                            chain_slug=chain_slug,
                            chain_id=chain_id,
                            contract_address=contract,
                        )
                        if dau_data.get("active_addresses", 0) > 0:
                            stats["dau_collected"] += 1
                    except Exception as dau_err:
                        logger.debug(f"DAU collection failed for {coin_id}: {dau_err}")
                
                # Collect top holders
                if contract:
                    try:
                        holders = await collector.collect_top_holders(
                            coin_id=coin_id,
                            chain_slug=chain_slug,
                            chain_id=chain_id,
                            contract_address=contract,
                            limit=50,
                        )
                        if holders:
                            stats["holders_collected"] += 1
                    except Exception as holder_err:
                        logger.debug(f"Holder collection failed for {coin_id}: {holder_err}")
                
                # Always update signals (even if no new whale txs, to calculate from existing data)
                updated = await collector.update_onchain_signals(coin_id, whale_txs if whale_txs else None)
                if updated:
                    stats["signals_updated"] += 1
                
                stats["coins_processed"] += 1
                
                # Small delay between coins to avoid rate limiting
                await asyncio.sleep(0.5)
                
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
    Pre-compute multi-horizon ASI for top 100 coins.
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
        
        # Get top 100 coins by market cap (Tier 1)
        coins = db.get_market_data(limit=100, orderby="market_cap")
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
    Pre-compute multi-horizon ASI for coins ranked 101-500.
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
        
        logger.info("Scheduler: Starting Multi-Horizon Tier 2 (coins 101-500) job...")
        
        db = get_database_service()
        settings = get_settings()
        
        # Ensure cache table exists
        db.ensure_multi_horizon_table()
        
        analyzer = AnalyzerService(db, settings)
        
        # Get coins 101-500 by market cap (skip first 100, take next 400)
        all_coins = db.get_market_data(limit=500, orderby="market_cap")
        tier2_coins = all_coins[100:]  # Skip top 100 (handled by Tier 1)
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
            "tier": "101-500",
        }
        
        logger.info(f"Scheduler: Multi-Horizon Tier 2 complete - computed {computed}/{len(coin_ids)}, failed {failed}")
        
    except Exception as e:
        logger.error(f"Scheduler: Multi-Horizon Tier 2 job failed - {e}")
        state["last_result"] = {"error": str(e)}
    finally:
        state["is_running"] = False


async def run_discovery_engine_job():
    """Background job to update market discovery snapshot."""
    state = SCHEDULER_STATE["discovery_engine"]
    
    if state["is_running"]:
        logger.warning("Discovery engine job already running, skipping")
        return
    
    state["is_running"] = True
    state["last_run"] = datetime.now().isoformat()
    
    try:
        from app.services.database import get_database_service
        from app.services.discovery_engine import DiscoveryEngine
        
        logger.info("Scheduler: Starting Discovery Engine job...")
        
        db = get_database_service()
        engine = DiscoveryEngine(db)
        
        result = await engine.update_snapshot()
        
        state["last_result"] = result
        
        logger.info(f"Scheduler: Discovery Engine complete - {result}")
        
    except Exception as e:
        logger.error(f"Scheduler: Discovery Engine job failed - {e}")
        state["last_result"] = {"error": str(e)}
    finally:
        state["is_running"] = False


async def run_gems_tracker_job():
    """
    Background job to track hidden gems performance.
    
    1. Save newly detected gems to hidden_gems_history table
    2. Evaluate performance of gems detected 7d and 30d ago
    3. Update success/failed status
    """
    state = SCHEDULER_STATE["gems_tracker"]
    
    if state["is_running"]:
        logger.warning("Gems tracker job already running, skipping")
        return
    
    state["is_running"] = True
    state["last_run"] = datetime.now().isoformat()
    
    try:
        from sqlalchemy import text
        from app.services.database import get_database_service
        
        logger.info("Scheduler: Starting Gems Tracker job...")
        
        db = get_database_service()
        stats = {
            "new_gems_saved": 0,
            "gems_evaluated_7d": 0,
            "gems_evaluated_30d": 0,
            "successes": 0,
            "failures": 0,
        }
        
        with db.engine.connect() as conn:
            # 1. Save new gems to history (those not already saved today)
            save_query = text("""
                INSERT INTO hidden_gems_history (
                    coin_id, symbol, name, detected_at, detection_price,
                    discovery_score, signal_strength, confirmation_count,
                    pattern_name, divergence_type, rs_vs_btc, rs_vs_market,
                    volume_ratio, is_accumulating
                )
                SELECT 
                    coin_id, symbol, name, NOW(), price,
                    discovery_score, signal_strength, confirmation_count,
                    pattern_name, divergence_type, rs_vs_btc, rs_vs_market,
                    volume_ratio, COALESCE(is_accumulating, FALSE)
                FROM market_discovery_snapshot
                WHERE discovery_score >= 75
                  AND confirmation_count >= 2
                  AND market_cap_rank > 50
                  AND (is_outperformer = TRUE OR is_accumulating = TRUE)
                  AND change_24h < 30
                  AND volume_24h > 100000
                ON CONFLICT (coin_id, DATE(detected_at)) DO NOTHING
                RETURNING coin_id
            """)
            result = conn.execute(save_query)
            stats["new_gems_saved"] = result.rowcount
            
            # 2. Get BTC price change for comparison
            btc_query = text("""
                SELECT change_7d, change_24h * 30 / 100 as approx_30d
                FROM market_discovery_snapshot
                WHERE symbol = 'BTC' LIMIT 1
            """)
            btc_result = conn.execute(btc_query).fetchone()
            btc_return_7d = float(btc_result[0]) if btc_result and btc_result[0] else 0
            btc_return_30d = float(btc_result[1]) if btc_result and btc_result[1] else 0
            
            # 3. Evaluate gems from 7 days ago
            eval_7d_query = text("""
                UPDATE hidden_gems_history h
                SET 
                    price_7d = c.price,
                    return_7d = CASE 
                        WHEN h.detection_price > 0 THEN 
                            ((c.price - h.detection_price) / h.detection_price * 100)
                        ELSE 0 
                    END,
                    btc_return_7d = :btc_return_7d,
                    evaluated_at = NOW()
                FROM aihub_coins c
                WHERE h.coin_id = c.coin_id
                  AND h.detected_at >= NOW() - INTERVAL '8 days'
                  AND h.detected_at < NOW() - INTERVAL '6 days'
                  AND h.price_7d IS NULL
                RETURNING h.coin_id
            """)
            result = conn.execute(eval_7d_query, {"btc_return_7d": btc_return_7d})
            stats["gems_evaluated_7d"] = result.rowcount
            
            # 4. Evaluate gems from 30 days ago and set final status
            eval_30d_query = text("""
                UPDATE hidden_gems_history h
                SET 
                    price_30d = c.price,
                    return_30d = CASE 
                        WHEN h.detection_price > 0 THEN 
                            ((c.price - h.detection_price) / h.detection_price * 100)
                        ELSE 0 
                    END,
                    btc_return_30d = :btc_return_30d,
                    status = CASE
                        WHEN ((c.price - h.detection_price) / NULLIF(h.detection_price, 0) * 100) > 25 THEN 'success'
                        WHEN ((c.price - h.detection_price) / NULLIF(h.detection_price, 0) * 100) < -20 THEN 'failed'
                        ELSE 'neutral'
                    END,
                    evaluated_at = NOW()
                FROM aihub_coins c
                WHERE h.coin_id = c.coin_id
                  AND h.detected_at >= NOW() - INTERVAL '31 days'
                  AND h.detected_at < NOW() - INTERVAL '29 days'
                  AND h.price_30d IS NULL
                RETURNING h.coin_id, h.status
            """)
            result = conn.execute(eval_30d_query, {"btc_return_30d": btc_return_30d})
            rows = result.fetchall()
            stats["gems_evaluated_30d"] = len(rows)
            stats["successes"] = sum(1 for r in rows if r[1] == 'success')
            stats["failures"] = sum(1 for r in rows if r[1] == 'failed')
            
            conn.commit()
        
        state["last_result"] = stats
        logger.info(f"Scheduler: Gems Tracker complete - {stats}")
        
    except Exception as e:
        logger.error(f"Scheduler: Gems Tracker job failed - {e}")
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
    
    # Increase misfire_grace_time to 60 seconds to prevent jobs from being skipped
    # when delayed due to other jobs running concurrently
    _scheduler = AsyncIOScheduler(
        job_defaults={
            'coalesce': True,  # Combine multiple missed runs into one
            'max_instances': 1,  # Only one instance of each job at a time
            'misfire_grace_time': 60  # Allow 60 seconds delay before marking as missed
        }
    )
    
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
    
    # Add On-chain Collector job - every 30 minutes (staggered by 5 seconds to avoid collision)
    if SCHEDULER_STATE["onchain_collector"]["enabled"]:
        from datetime import timedelta
        _scheduler.add_job(
            run_onchain_job,
            trigger=IntervalTrigger(
                minutes=SCHEDULER_STATE["onchain_collector"]["interval_minutes"],
                start_date=datetime.now() + timedelta(seconds=15)  # Start 15 seconds after other jobs
            ),
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
    
    # Add Discovery Engine job - Market Gainers/Losers snapshot
    if SCHEDULER_STATE["discovery_engine"]["enabled"]:
        _scheduler.add_job(
            run_discovery_engine_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["discovery_engine"]["interval_minutes"]),
            id="discovery_engine_job",
            name="Market Discovery Snapshot Update",
            replace_existing=True,
        )
        logger.info(f"Scheduled Discovery Engine job: every {SCHEDULER_STATE['discovery_engine']['interval_minutes']} minutes")
    
    # Add Gems Tracker job - every 6 hours
    if SCHEDULER_STATE["gems_tracker"]["enabled"]:
        _scheduler.add_job(
            run_gems_tracker_job,
            trigger=IntervalTrigger(minutes=SCHEDULER_STATE["gems_tracker"]["interval_minutes"]),
            id="gems_tracker_job",
            name="Hidden Gems Performance Tracker",
            replace_existing=True,
        )
        logger.info(f"Scheduled Gems Tracker job: every {SCHEDULER_STATE['gems_tracker']['interval_minutes']} minutes")
    
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
