#!/usr/bin/env python3
"""
Fetch Contract Addresses from CoinGecko
Automatically populates tokens_on_chain table with contract addresses for all coins in DB
"""
import asyncio
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import text
from app.core.config import settings
from app.services.database import DatabaseService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CoinGecko API
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Chain ID mapping (CoinGecko platform -> our chain_id)
CHAIN_MAPPING = {
    'ethereum': 1,
    'binance-smart-chain': 56,
    'polygon-pos': 137,
    'arbitrum-one': 42161,
    'optimistic-ethereum': 10,
    'avalanche': 43114,
    'base': 8453,
    'fantom': 250,
}


def get_all_coins(db: DatabaseService) -> list:
    """Get all coin_ids from aihub_coins table"""
    query = text("SELECT coin_id FROM aihub_coins ORDER BY market_cap DESC NULLS LAST")
    with db.get_session() as session:
        rows = session.execute(query).fetchall()
        return [row[0] for row in rows]


async def fetch_coin_details(client: httpx.AsyncClient, coin_id: str) -> dict:
    """Fetch coin details from CoinGecko including contract addresses"""
    try:
        url = f"{COINGECKO_API}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        
        response = await client.get(url, params=params)
        
        if response.status_code == 429:
            logger.warning("Rate limited, waiting 60s...")
            await asyncio.sleep(60)
            return await fetch_coin_details(client, coin_id)
            
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {coin_id}: {response.status_code}")
            return None
            
        return response.json()
        
    except Exception as e:
        logger.error(f"Error fetching {coin_id}: {e}")
        return None


def extract_contracts(coin_data: dict) -> list:
    """Extract contract addresses from CoinGecko response"""
    contracts = []
    
    if not coin_data:
        return contracts
        
    platforms = coin_data.get("platforms", {})
    detail_platforms = coin_data.get("detail_platforms", {})
    
    for platform, address in platforms.items():
        if not address or platform == "":
            continue
            
        chain_id = CHAIN_MAPPING.get(platform)
        if not chain_id:
            continue
            
        # Get decimals from detail_platforms if available
        decimals = 18
        if platform in detail_platforms:
            decimals = detail_platforms[platform].get("decimal_place", 18)
            
        contracts.append({
            "platform": platform,
            "chain_id": chain_id,
            "contract_address": address.lower(),
            "decimals": decimals,
        })
        
    return contracts


def save_contract(db: DatabaseService, coin_id: str, symbol: str, name: str, contract: dict):
    """Save contract to tokens_on_chain table"""
    try:
        query = text("""
            INSERT INTO tokens_on_chain (coin_id, chain_id, contract_address, token_symbol, token_name, decimals)
            VALUES (:coin_id, :chain_id, :contract_address, :symbol, :name, :decimals)
            ON CONFLICT (chain_id, contract_address) DO UPDATE SET
                coin_id = EXCLUDED.coin_id,
                token_symbol = EXCLUDED.token_symbol,
                token_name = EXCLUDED.token_name,
                decimals = EXCLUDED.decimals,
                updated_at = NOW()
        """)
        
        with db.get_session() as session:
            session.execute(query, {
                "coin_id": coin_id,
                "chain_id": contract["chain_id"],
                "contract_address": contract["contract_address"],
                "symbol": symbol,
                "name": name,
                "decimals": contract["decimals"],
            })
            session.commit()
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to save contract for {coin_id}: {e}")
        return False


async def main():
    logger.info("=" * 60)
    logger.info("Contract Address Fetcher")
    logger.info("=" * 60)
    
    database_url = settings.DATABASE_URL
    if not database_url:
        logger.error("No DATABASE_URL found")
        return
        
    db = DatabaseService(database_url)
    
    if not db.test_connection():
        logger.error("Failed to connect to database")
        return
        
    # Get all coins (sync function)
    coins = get_all_coins(db)
    logger.info(f"Found {len(coins)} coins in database")
    
    # Fetch contracts for each coin
    saved = 0
    skipped = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, coin_id in enumerate(coins, 1):
            logger.info(f"[{i}/{len(coins)}] Fetching {coin_id}...")
            
            coin_data = await fetch_coin_details(client, coin_id)
            
            if not coin_data:
                skipped += 1
                continue
                
            symbol = coin_data.get("symbol", "").upper()
            name = coin_data.get("name", "")
            contracts = extract_contracts(coin_data)
            
            if not contracts:
                logger.info(f"  No contracts found for {coin_id}")
                skipped += 1
                continue
                
            for contract in contracts:
                success = save_contract(db, coin_id, symbol, name, contract)
                if success:
                    saved += 1
                    logger.info(f"  Saved: {contract['platform']} -> {contract['contract_address'][:20]}...")
                    
            # Rate limit: CoinGecko free tier = 10-30 calls/min
            await asyncio.sleep(2)
            
    logger.info("=" * 60)
    logger.info(f"COMPLETE: Saved {saved} contracts, skipped {skipped} coins")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
