"""
Multi-Source Coin Data Fetcher Service
Fetches cryptocurrency data from multiple APIs concurrently
- CoinGecko
- Binance
- CoinCap
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import httpx

logger = logging.getLogger(__name__)


class CoinGeckoFetcher:
    """CoinGecko API"""
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session: Optional[httpx.AsyncClient] = None
    
    async def get_session(self) -> httpx.AsyncClient:
        if not self.session:
            headers = {"accept": "application/json"}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key
            self.session = httpx.AsyncClient(timeout=30.0, headers=headers)
        return self.session
    
    async def fetch_markets(self, page: int = 1, per_page: int = 250) -> List[Dict]:
        client = await self.get_session()
        try:
            response = await client.get(f"{self.BASE_URL}/coins/markets", params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": page,
                "sparkline": "false",
                "price_change_percentage": "1h,24h,7d"
            })
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"CoinGecko error: {e}")
        return []
    
    async def fetch_all_markets(self, max_coins: int = 5000) -> List[Dict]:
        """Fetch all pages with rate limiting - 3 pages at a time with delay"""
        pages_needed = (max_coins // 250) + 1
        all_coins = []
        
        # Fetch in batches of 3 pages to avoid rate limit (429)
        batch_size = 3
        for i in range(1, pages_needed + 1, batch_size):
            batch_pages = list(range(i, min(i + batch_size, pages_needed + 1)))
            tasks = [self.fetch_markets(page=p) for p in batch_pages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_coins.extend(result)
            
            # Wait between batches to respect rate limit
            if i + batch_size <= pages_needed:
                await asyncio.sleep(2)
        
        return all_coins[:max_coins]
    
    async def fetch_coin_details(self, coin_id: str) -> Optional[Dict]:
        """
        Fetch detailed coin info including contract addresses from CoinGecko
        
        Returns:
            Dict with platforms (contract addresses per chain) and other details
        """
        client = await self.get_session()
        try:
            await asyncio.sleep(0.25)  # Rate limiting
            response = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "false",
                    "community_data": "false",
                    "developer_data": "false",
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "coin_id": coin_id,
                    "symbol": data.get("symbol", "").upper(),
                    "name": data.get("name", ""),
                    "platforms": data.get("platforms", {}),  # {chain_slug: contract_address}
                    "categories": data.get("categories", []),
                    "asset_platform_id": data.get("asset_platform_id"),
                }
            elif response.status_code == 429:
                logger.warning(f"CoinGecko rate limit for {coin_id}")
                await asyncio.sleep(5)  # Wait on rate limit
        except Exception as e:
            logger.error(f"CoinGecko coin details error for {coin_id}: {e}")
        return None
    
    async def populate_contract_addresses(
        self,
        db,
        coin_ids: List[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Fetch and save contract addresses for coins from CoinGecko
        
        Args:
            db: DatabaseService instance
            coin_ids: List of specific coin_ids to update, or None for top coins
            limit: Number of coins to process if coin_ids not provided
            
        Returns:
            Stats dict with updated count
        """
        # Chain slug to chain_id mapping for Etherscan V2
        CHAIN_MAPPING = {
            "ethereum": 1,
            "binance-smart-chain": 56,
            "polygon-pos": 137,
            "arbitrum-one": 42161,
            "optimistic-ethereum": 10,
            "avalanche": 43114,
            "base": 8453,
            "fantom": 250,
        }
        
        updated = 0
        errors = 0
        
        # Get coins to update
        if not coin_ids:
            query = """
                SELECT coin_id FROM aihub_coins 
                WHERE contract_address IS NULL OR contract_address = ''
                ORDER BY market_cap DESC NULLS LAST
                LIMIT $1
            """
            rows = await db.fetch_all(query, limit)
            coin_ids = [row["coin_id"] for row in rows]
        
        logger.info(f"Populating contract addresses for {len(coin_ids)} coins")
        
        for coin_id in coin_ids:
            try:
                details = await self.fetch_coin_details(coin_id)
                
                if not details or not details.get("platforms"):
                    continue
                
                platforms = details["platforms"]
                
                # Find best platform (prefer ethereum, then others)
                contract_address = None
                chain_slug = None
                chain_id = None
                
                for platform_slug, address in platforms.items():
                    if not address:  # Skip empty addresses (native tokens)
                        continue
                    
                    # Check if we support this chain
                    if platform_slug in CHAIN_MAPPING:
                        contract_address = address
                        chain_slug = platform_slug
                        chain_id = CHAIN_MAPPING[platform_slug]
                        
                        # Prefer Ethereum if available
                        if platform_slug == "ethereum":
                            break
                
                if contract_address:
                    # Update database
                    update_query = """
                        UPDATE aihub_coins 
                        SET contract_address = $2, 
                            chain_slug = $3,
                            chain_id = $4,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE coin_id = $1
                    """
                    await db.execute(update_query, coin_id, contract_address, chain_slug, chain_id)
                    updated += 1
                    logger.debug(f"Updated {coin_id}: {chain_slug} -> {contract_address[:20]}...")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Failed to update {coin_id}: {e}")
        
        logger.info(f"Contract address population complete: {updated} updated, {errors} errors")
        
        return {
            "updated": updated,
            "errors": errors,
            "total_processed": len(coin_ids),
        }


class BinanceFetcher:
    """Binance API - Real-time prices"""
    BASE_URL = "https://api.binance.com/api/v3"
    
    async def fetch_24h_tickers(self) -> List[Dict]:
        """Fetch all 24h ticker data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/ticker/24hr")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Binance error: {e}")
        return []
    
    async def fetch_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List:
        """Fetch OHLCV klines"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/klines", params={
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit
                })
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Binance klines error for {symbol}: {e}")
        return []


class CoinCapFetcher:
    """CoinCap API - Alternative source"""
    BASE_URL = "https://api.coincap.io/v2"
    
    async def fetch_assets(self, limit: int = 2000) -> List[Dict]:
        """Fetch assets list"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/assets", params={
                    "limit": limit
                })
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"CoinCap error: {e}")
        return []


class OKXFetcher:
    """OKX Exchange API"""
    BASE_URL = "https://www.okx.com/api/v5"
    
    async def fetch_tickers(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/market/tickers", params={
                    "instType": "SPOT"
                })
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"OKX error: {e}")
        return []


class BybitFetcher:
    """Bybit Exchange API"""
    BASE_URL = "https://api.bybit.com/v5"
    
    async def fetch_tickers(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/market/tickers", params={
                    "category": "spot"
                })
                if response.status_code == 200:
                    data = response.json()
                    return data.get("result", {}).get("list", [])
        except Exception as e:
            logger.error(f"Bybit error: {e}")
        return []


class KuCoinFetcher:
    """KuCoin Exchange API"""
    BASE_URL = "https://api.kucoin.com/api/v1"
    
    async def fetch_tickers(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/market/allTickers")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("ticker", [])
        except Exception as e:
            logger.error(f"KuCoin error: {e}")
        return []


class GateFetcher:
    """Gate.io Exchange API"""
    BASE_URL = "https://api.gateio.ws/api/v4"
    
    async def fetch_tickers(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/spot/tickers")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Gate.io error: {e}")
        return []


class GeckoTerminalFetcher:
    """GeckoTerminal API - DEX data"""
    BASE_URL = "https://api.geckoterminal.com/api/v2"
    
    async def fetch_trending_pools(self, network: str = "eth") -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/networks/{network}/trending_pools")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"GeckoTerminal error: {e}")
        return []


class DexScreenerFetcher:
    """DexScreener API - DEX aggregator"""
    BASE_URL = "https://api.dexscreener.com"
    
    async def fetch_token_profiles(self) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/token-profiles/latest/v1")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"DexScreener error: {e}")
        return []
    
    async def search_pairs(self, query: str) -> List[Dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.BASE_URL}/latest/dex/search", params={"q": query})
                if response.status_code == 200:
                    data = response.json()
                    return data.get("pairs", [])
        except Exception as e:
            logger.error(f"DexScreener search error: {e}")
        return []


class MultiSourceFetcher:
    """Aggregates data from 10 sources concurrently"""
    
    def __init__(self, db_service, coingecko_key: str = ""):
        self.db = db_service
        # CEX Sources
        self.coingecko = CoinGeckoFetcher(coingecko_key)
        self.binance = BinanceFetcher()
        self.okx = OKXFetcher()
        self.bybit = BybitFetcher()
        self.kucoin = KuCoinFetcher()
        self.gate = GateFetcher()
        # Aggregators
        self.coincap = CoinCapFetcher()
        # DEX Sources
        self.geckoterminal = GeckoTerminalFetcher()
        self.dexscreener = DexScreenerFetcher()
    
    async def fetch_all_concurrent(self) -> Dict[str, Any]:
        """Fetch from all 10 sources concurrently"""
        start = datetime.now()
        
        # Run ALL fetchers in parallel
        tasks = {
            # Primary data sources
            "coingecko": self.coingecko.fetch_all_markets(5000),
            "coincap": self.coincap.fetch_assets(2000),
            # CEX real-time prices
            "binance": self.binance.fetch_24h_tickers(),
            "okx": self.okx.fetch_tickers(),
            "bybit": self.bybit.fetch_tickers(),
            "kucoin": self.kucoin.fetch_tickers(),
            "gate": self.gate.fetch_tickers(),
            # DEX data
            "geckoterminal": self.geckoterminal.fetch_trending_pools("eth"),
            "dexscreener": self.dexscreener.fetch_token_profiles(),
        }
        
        results = {}
        gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for key, result in zip(tasks.keys(), gathered):
            if isinstance(result, Exception):
                logger.error(f"{key} failed: {result}")
                results[key] = []
            else:
                results[key] = result
                logger.info(f"{key}: {len(result) if isinstance(result, list) else 0} items")
        
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"Fetched from {len(tasks)} sources in {duration:.2f}s")
        
        return results
    
    async def merge_and_save(self, data: Dict[str, List]) -> Dict[str, int]:
        """Merge data from all sources and save to DB"""
        from sqlalchemy import text
        
        stats = {"total": 0, "saved": 0, "updated": 0, "source": "none"}
        
        # Primary: CoinGecko (most complete data)
        coins_map = {}
        
        for coin in data.get("coingecko", []):
            coin_id = coin.get("id")
            if coin_id:
                coins_map[coin_id] = {
                    "coin_id": coin_id,
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "image": coin.get("image"),
                    "current_price": coin.get("current_price"),
                    "market_cap": coin.get("market_cap"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_change_24h": coin.get("price_change_24h"),
                    "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                    "price_change_percentage_1h": coin.get("price_change_percentage_1h_in_currency"),
                    "price_change_percentage_7d": coin.get("price_change_percentage_7d_in_currency"),
                    "total_volume": coin.get("total_volume"),
                    "high_24h": coin.get("high_24h"),
                    "low_24h": coin.get("low_24h"),
                    "source": "coingecko",
                }
        
        # FALLBACK: If CoinGecko failed, use Binance data directly
        if len(coins_map) == 0:
            logger.warning("CoinGecko returned 0 items, using Binance as fallback")
            
            for ticker in data.get("binance", []):
                symbol = ticker.get("symbol", "")
                if symbol.endswith("USDT"):
                    base = symbol[:-4].upper()
                    price = float(ticker.get("lastPrice", 0) or 0)
                    if price > 0:
                        coins_map[base.lower()] = {
                            "coin_id": base.lower(),
                            "symbol": base,
                            "name": base,
                            "image": "",
                            "current_price": price,
                            "market_cap": 0,
                            "market_cap_rank": 0,
                            "price_change_percentage_24h": float(ticker.get("priceChangePercent", 0) or 0),
                            "total_volume": float(ticker.get("quoteVolume", 0) or 0),
                            "high_24h": float(ticker.get("highPrice", 0) or 0),
                            "low_24h": float(ticker.get("lowPrice", 0) or 0),
                            "source": "binance",
                        }
            stats["source"] = "binance_fallback"
        else:
            stats["source"] = "coingecko"
        
        # Enrich with Binance real-time prices
        binance_map = {}
        for ticker in data.get("binance", []):
            symbol = ticker.get("symbol", "")
            if symbol.endswith("USDT"):
                base = symbol[:-4]
                binance_map[base] = {
                    "price": float(ticker.get("lastPrice", 0) or 0),
                    "volume": float(ticker.get("volume", 0) or 0),
                    "change_24h": float(ticker.get("priceChangePercent", 0) or 0),
                }
        
        # Update prices from Binance (more real-time)
        for coin_id, coin_data in coins_map.items():
            symbol = coin_data.get("symbol", "")
            if symbol in binance_map:
                binance_data = binance_map[symbol]
                # Only update if Binance has valid data
                if binance_data["price"] > 0:
                    coin_data["current_price"] = binance_data["price"]
                    if coin_data.get("source") == "coingecko":
                        coin_data["source"] = "binance+coingecko"
        
        stats["total"] = len(coins_map)
        
        # Skip save if no data (preserve existing DB records)
        if stats["total"] == 0:
            logger.warning("No data to save, skipping to preserve existing records")
            return stats
        
        # Batch insert/update - matching existing schema
        query = text("""
            INSERT INTO aihub_coins (
                symbol, name, image_url, price, change_24h, volume_24h,
                market_cap, rank, high_24h, low_24h, coin_id, last_updated
            ) VALUES (
                :symbol, :name, :image_url, :price, :change_24h, :volume_24h,
                :market_cap, :rank, :high_24h, :low_24h, :coin_id, :last_updated
            )
            ON CONFLICT (symbol) DO UPDATE SET
                name = COALESCE(NULLIF(EXCLUDED.name, ''), aihub_coins.name),
                image_url = COALESCE(NULLIF(EXCLUDED.image_url, ''), aihub_coins.image_url),
                price = EXCLUDED.price,
                change_24h = EXCLUDED.change_24h,
                volume_24h = EXCLUDED.volume_24h,
                market_cap = CASE WHEN EXCLUDED.market_cap > 0 THEN EXCLUDED.market_cap ELSE aihub_coins.market_cap END,
                rank = CASE WHEN EXCLUDED.rank > 0 THEN EXCLUDED.rank ELSE aihub_coins.rank END,
                high_24h = EXCLUDED.high_24h,
                low_24h = EXCLUDED.low_24h,
                coin_id = COALESCE(NULLIF(EXCLUDED.coin_id, ''), aihub_coins.coin_id),
                last_updated = EXCLUDED.last_updated
        """)
        
        try:
            with self.db.engine.begin() as conn:
                for coin_data in coins_map.values():
                    # Map from CoinGecko format to DB schema
                    conn.execute(query, {
                        "symbol": coin_data.get("symbol", "").upper(),
                        "name": coin_data.get("name", ""),
                        "image_url": coin_data.get("image", ""),
                        "price": coin_data.get("current_price", 0) or 0,
                        "change_24h": coin_data.get("price_change_percentage_24h", 0) or 0,
                        "volume_24h": coin_data.get("total_volume", 0) or 0,
                        "market_cap": coin_data.get("market_cap", 0) or 0,
                        "rank": coin_data.get("market_cap_rank", 0) or 0,
                        "high_24h": coin_data.get("high_24h", 0) or 0,
                        "low_24h": coin_data.get("low_24h", 0) or 0,
                        "coin_id": coin_data.get("coin_id", ""),
                        "last_updated": datetime.now()
                    })
                    stats["saved"] += 1
        except Exception as e:
            logger.error(f"Batch save failed: {e}")
        
        return stats
    
    async def fetch_ohlcv_concurrent(self, symbols: List[str], limit: int = 5000) -> Dict[str, int]:
        """Fetch OHLCV from Binance for ALL symbols concurrently (no Supabase limit)"""
        from sqlalchemy import text
        
        stats = {"fetched": 0, "saved": 0, "failed": 0}
        
        # Larger batch size for Proxmox (no rate limit worries with local DB)
        batch_size = 20
        total = min(len(symbols), limit)
        
        logger.info(f"Fetching OHLCV for {total} coins...")
        
        for i in range(0, total, batch_size):
            batch = symbols[i:i + batch_size]
            tasks = [self.binance.fetch_klines(f"{sym}USDT", "1h", 100) for sym in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for sym, result in zip(batch, results):
                if isinstance(result, Exception):
                    stats["failed"] += 1
                elif isinstance(result, list) and len(result) > 0:
                    stats["fetched"] += 1
                    saved = await self._save_klines(sym, result)
                    if saved:
                        stats["saved"] += 1
            
            # Progress log every 100 coins
            if (i + batch_size) % 100 == 0:
                logger.info(f"OHLCV progress: {i + batch_size}/{total}")
        
        logger.info(f"OHLCV complete: {stats['saved']}/{stats['fetched']} saved")
        return stats
    
    async def _save_klines(self, symbol: str, klines: List) -> bool:
        """Save Binance klines to aihub_ohlcv"""
        from sqlalchemy import text
        
        # Schema: symbol, timeframe (1=1h), open_time, open, high, low, close, volume
        query = text("""
            INSERT INTO aihub_ohlcv (symbol, timeframe, open_time, open, high, low, close, volume)
            VALUES (:symbol, :timeframe, :open_time, :open, :high, :low, :close, :volume)
            ON CONFLICT DO NOTHING
        """)
        
        try:
            with self.db.engine.begin() as conn:
                for k in klines:
                    # Binance kline: [open_time, open, high, low, close, volume, ...]
                    if len(k) >= 6:
                        conn.execute(query, {
                            "symbol": symbol.upper(),
                            "timeframe": 1,  # 1h = 1
                            "open_time": datetime.fromtimestamp(k[0] / 1000),
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5]),
                        })
            return True
        except Exception as e:
            logger.error(f"OHLCV save failed for {symbol}: {e}")
            return False


class DataFetcherService:
    """Main service - backwards compatible interface"""
    
    def __init__(self, db_service, coingecko_api_key: str = ""):
        self.db = db_service
        self.multi_fetcher = MultiSourceFetcher(db_service, coingecko_api_key)
    
    async def fetch_and_save_coins(self) -> Dict[str, Any]:
        """Fetch from all sources and save"""
        from app.services.monitoring import increment_counter, record_duration
        import time
        
        start = time.time()
        
        # Fetch concurrently from all sources
        data = await self.multi_fetcher.fetch_all_concurrent()
        
        # Merge and save
        stats = await self.multi_fetcher.merge_and_save(data)
        
        duration = time.time() - start
        logger.info(f"Multi-source fetch complete: {stats['saved']}/{stats['total']} in {duration:.2f}s")
        
        # Metrics
        increment_counter("fetch_total")
        record_duration("fetch", duration)
        
        return {"fetched": stats["total"], "saved": stats["saved"], "duration": duration}
    
    async def fetch_ohlcv_for_all_coins(self, limit: int = 5000) -> Dict[str, Any]:
        """Fetch OHLCV for ALL coins from Binance (Proxmox has no limits!)"""
        from sqlalchemy import text
        
        # Get ALL symbols with market cap
        query = text("""
            SELECT symbol FROM aihub_coins 
            WHERE market_cap > 0 
            ORDER BY market_cap DESC 
            LIMIT :limit
        """)
        
        with self.db.engine.connect() as conn:
            rows = conn.execute(query, {"limit": limit}).fetchall()
        
        symbols = [row[0] for row in rows]
        logger.info(f"Fetching OHLCV for {len(symbols)} coins (Proxmox unlimited)")
        
        stats = await self.multi_fetcher.fetch_ohlcv_concurrent(symbols, limit)
        
        return stats
    
    # Backwards compatible alias
    async def fetch_ohlcv_for_top_coins(self, limit: int = 5000) -> Dict[str, Any]:
        return await self.fetch_ohlcv_for_all_coins(limit)


# Singleton
_data_fetcher: Optional[DataFetcherService] = None


def get_data_fetcher() -> DataFetcherService:
    global _data_fetcher
    if _data_fetcher is None:
        from app.services.database import get_db_service
        from app.core.config import get_settings
        settings = get_settings()
        
        coingecko_key = getattr(settings, 'coingecko_api_key', '')
        _data_fetcher = DataFetcherService(get_db_service(), coingecko_key)
    
    return _data_fetcher
