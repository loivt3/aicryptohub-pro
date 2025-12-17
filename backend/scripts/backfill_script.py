#!/usr/bin/env python3
"""
Backfill Script for On-Chain Historical Data
AI Crypto Hub Pro

This script seeds historical on-chain data (DAU, whale txs) for all coins
in the database that have contract addresses. Run this once after deploying
a new instance or adding new coins.

Usage:
    python backfill_script.py [--days 7] [--coin-id bitcoin]
"""
import asyncio
import argparse
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.database import DatabaseService
from app.services.onchain_collector import OnChainCollector, CHAIN_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def get_coins_with_contracts(db: DatabaseService) -> list:
    """
    Get all coins that have contract addresses defined
    
    Returns:
        List of coin dicts with coin_id, chain_slug, chain_id, contract_address
    """
    query = """
        SELECT 
            t.coin_id,
            c.slug as chain_slug,
            c.chain_id,
            t.contract_address,
            t.decimals
        FROM tokens_on_chain t
        JOIN chains c ON t.chain_id = c.id
        WHERE t.contract_address IS NOT NULL
        AND t.contract_address != ''
        ORDER BY t.coin_id
    """
    
    rows = await db.fetch_all(query)
    
    coins = []
    for row in rows:
        coins.append({
            'coin_id': row['coin_id'],
            'chain_slug': row['chain_slug'],
            'chain_id': row['chain_id'],
            'contract_address': row['contract_address'],
            'decimals': row['decimals'] or 18,
        })
        
    return coins


async def check_existing_data(db: DatabaseService, coin_id: str) -> int:
    """
    Check how many days of DAU data exists for a coin
    
    Returns:
        Number of days with data
    """
    query = """
        SELECT COUNT(DISTINCT date) as days
        FROM daily_active_addresses
        WHERE coin_id = $1
    """
    
    result = await db.fetch_one(query, coin_id)
    return result['days'] if result else 0


async def backfill_coin(
    collector: OnChainCollector,
    coin: dict,
    days: int = 7,
    force: bool = False,
) -> dict:
    """
    Backfill historical data for a single coin
    
    Args:
        collector: OnChainCollector instance
        coin: Coin dict with coin_id, chain_slug, chain_id, contract_address
        days: Number of days to backfill
        force: Force backfill even if data exists
        
    Returns:
        Summary dict
    """
    coin_id = coin['coin_id']
    
    # Check existing data
    if not force:
        existing = await check_existing_data(collector.db, coin_id)
        if existing >= days:
            logger.info(f"Skipping {coin_id}: already has {existing} days of data")
            return {
                'coin_id': coin_id,
                'status': 'skipped',
                'reason': f'already has {existing} days',
            }
            
    logger.info(f"Backfilling {days} days for {coin_id}...")
    
    try:
        result = await collector.seed_historical_data(
            coin_id=coin['coin_id'],
            chain_slug=coin['chain_slug'],
            chain_id=coin['chain_id'],
            contract_address=coin['contract_address'],
            days=days,
        )
        
        return {
            'coin_id': coin_id,
            'status': 'success',
            'days_seeded': result.get('days_seeded', 0),
        }
        
    except Exception as e:
        logger.error(f"Failed to backfill {coin_id}: {e}")
        return {
            'coin_id': coin_id,
            'status': 'error',
            'error': str(e),
        }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Backfill on-chain historical data for coins'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to backfill (default: 7)'
    )
    parser.add_argument(
        '--coin-id',
        type=str,
        default=None,
        help='Specific coin ID to backfill (default: all coins)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force backfill even if data exists'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only show what would be done'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("On-Chain Data Backfill Script")
    logger.info("=" * 60)
    
    # Initialize services
    logger.info("Connecting to database...")
    
    # Get database URL from settings
    database_url = settings.DATABASE_URL
    if not database_url:
        logger.error("No DATABASE_URL found in environment")
        return
        
    db = DatabaseService(database_url)
    await db.connect()
    
    try:
        # Get API key
        api_key = settings.ETHERSCAN_API_KEY
        if not api_key:
            logger.warning("No ETHERSCAN_API_KEY found, using limited rate")
            
        collector = OnChainCollector(db, api_key)
        
        # Load exchange addresses first
        await collector.load_exchange_addresses()
        
        # Get coins to process
        if args.coin_id:
            # Single coin mode
            query = """
                SELECT 
                    t.coin_id,
                    c.slug as chain_slug,
                    c.chain_id,
                    t.contract_address,
                    t.decimals
                FROM tokens_on_chain t
                JOIN chains c ON t.chain_id = c.id
                WHERE t.coin_id = $1
            """
            rows = await db.fetch_all(query, args.coin_id)
            coins = [{
                'coin_id': r['coin_id'],
                'chain_slug': r['chain_slug'],
                'chain_id': r['chain_id'],
                'contract_address': r['contract_address'],
                'decimals': r['decimals'] or 18,
            } for r in rows]
        else:
            coins = await get_coins_with_contracts(db)
            
        logger.info(f"Found {len(coins)} coins with contract addresses")
        
        if args.dry_run:
            logger.info("DRY RUN - would process:")
            for coin in coins:
                existing = await check_existing_data(db, coin['coin_id'])
                logger.info(f"  - {coin['coin_id']} ({coin['chain_slug']}) - {existing} days existing")
            return
            
        # Process all coins
        results = {
            'success': [],
            'skipped': [],
            'error': [],
        }
        
        for i, coin in enumerate(coins, 1):
            logger.info(f"Processing {i}/{len(coins)}: {coin['coin_id']}")
            
            result = await backfill_coin(
                collector,
                coin,
                days=args.days,
                force=args.force,
            )
            
            results[result['status']].append(result)
            
            # Rate limit between coins
            if i < len(coins):
                await asyncio.sleep(1)
                
        # Summary
        logger.info("=" * 60)
        logger.info("BACKFILL COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Success: {len(results['success'])} coins")
        logger.info(f"Skipped: {len(results['skipped'])} coins")
        logger.info(f"Errors:  {len(results['error'])} coins")
        
        if results['error']:
            logger.warning("Failed coins:")
            for r in results['error']:
                logger.warning(f"  - {r['coin_id']}: {r.get('error')}")
                
        # Cleanup
        await collector.close()
        
    finally:
        await db.disconnect()
        

if __name__ == "__main__":
    asyncio.run(main())
