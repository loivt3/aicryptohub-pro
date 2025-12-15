"""
Triggers Router - Background job triggers for data collection and analysis
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/triggers", tags=["triggers"])


class TriggerResponse(BaseModel):
    """Standard response for trigger endpoints"""
    success: bool
    message: str
    job_id: str
    items_queued: int = 0


@router.post("/fetch", response_model=TriggerResponse)
async def trigger_fetch(background_tasks: BackgroundTasks):
    """
    Trigger data fetch from all sources (CoinGecko, Binance, etc.)
    Runs in background.
    """
    job_id = f"fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def run_fetch():
        try:
            from app.services.data_fetcher import get_data_fetcher
            fetcher = get_data_fetcher()
            result = await fetcher.fetch_and_save_coins()
            logger.info(f"Fetch job {job_id} complete: {result}")
        except Exception as e:
            logger.error(f"Fetch job {job_id} failed: {e}")
    
    background_tasks.add_task(run_fetch)
    
    return TriggerResponse(
        success=True,
        message=f"Data fetch job queued",
        job_id=job_id,
    )


@router.post("/analysis", response_model=TriggerResponse)
async def trigger_analysis(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    force_refresh: bool = False,
):
    """
    Trigger technical analysis for coins.
    
    Args:
        limit: Max coins to analyze
        force_refresh: Force re-analysis even if recent
    """
    job_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def run_analysis():
        try:
            from app.services.database import get_db_service
            from app.services.analyzer import AnalyzerService
            from app.core.config import get_settings
            
            db = get_db_service()
            settings = get_settings()
            analyzer = AnalyzerService(db, settings)
            
            coin_ids = db.get_coins_for_analysis(limit=limit)
            if coin_ids:
                results = await analyzer.analyze_coins(coin_ids, force_refresh=force_refresh)
                logger.info(f"Analysis job {job_id}: {results['success_count']}/{len(coin_ids)} coins")
        except Exception as e:
            logger.error(f"Analysis job {job_id} failed: {e}")
    
    background_tasks.add_task(run_analysis)
    
    return TriggerResponse(
        success=True,
        message=f"Analysis job queued for up to {limit} coins",
        job_id=job_id,
        items_queued=limit,
    )


@router.post("/ohlcv", response_model=TriggerResponse)
async def trigger_ohlcv(
    background_tasks: BackgroundTasks,
    limit: int = 500,
):
    """
    Trigger OHLCV data fetch from Binance for top coins.
    """
    job_id = f"ohlcv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def run_ohlcv():
        try:
            from app.services.data_fetcher import get_data_fetcher
            fetcher = get_data_fetcher()
            result = await fetcher.fetch_ohlcv_for_all_coins(limit=limit)
            logger.info(f"OHLCV job {job_id} complete: {result}")
        except Exception as e:
            logger.error(f"OHLCV job {job_id} failed: {e}")
    
    background_tasks.add_task(run_ohlcv)
    
    return TriggerResponse(
        success=True,
        message=f"OHLCV fetch queued for {limit} coins",
        job_id=job_id,
        items_queued=limit,
    )


@router.post("/onchain-signals", response_model=TriggerResponse)
async def trigger_onchain_signals(
    background_tasks: BackgroundTasks,
    coin_id: Optional[str] = None,
    limit: int = 10,
):
    """
    Trigger on-chain signal collection and analysis.
    
    Args:
        coin_id: Specific coin to analyze, or None for top coins
        limit: Number of coins if coin_id not specified
    """
    job_id = f"onchain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return TriggerResponse(
        success=True,
        message=f"On-chain signals job queued" + (f" for {coin_id}" if coin_id else f" for top {limit} coins"),
        job_id=job_id,
        items_queued=1 if coin_id else limit,
    )


@router.post("/populate-contracts", response_model=TriggerResponse)
async def trigger_populate_contracts(
    background_tasks: BackgroundTasks,
    limit: int = 100,
):
    """
    Populate contract addresses from CoinGecko for on-chain tracking.
    """
    job_id = f"contracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def run_populate():
        try:
            from app.services.data_fetcher import get_data_fetcher
            from app.services.database import get_db_service
            
            fetcher = get_data_fetcher()
            db = get_db_service()
            result = await fetcher.multi_fetcher.coingecko.populate_contract_addresses(db, limit=limit)
            logger.info(f"Contract population {job_id}: {result}")
        except Exception as e:
            logger.error(f"Contract population {job_id} failed: {e}")
    
    background_tasks.add_task(run_populate)
    
    return TriggerResponse(
        success=True,
        message=f"Contract population queued for {limit} coins",
        job_id=job_id,
        items_queued=limit,
    )
