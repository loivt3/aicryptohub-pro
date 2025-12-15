"""
Multi-Source Price Aggregator Service

Fetches crypto price data from multiple APIs (Binance, OKX, CoinGecko)
with fallback strategy and caching.

Ported from WordPress: class-price-aggregator.php
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class PriceAggregator:
    """Multi-source cryptocurrency price aggregator with fallback strategy."""
    
    # API Endpoints
    BINANCE_TICKER_API = "https://api.binance.com/api/v3/ticker/24hr"
    OKX_TICKER_API = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    COINGECKO_MARKETS_API = "https://api.coingecko.com/api/v3/coins/markets"
    COINGECKO_GLOBAL_API = "https://api.coingecko.com/api/v3/global"
    
    # Configuration
    REQUEST_TIMEOUT = 15
    DEFAULT_COINS_LIMIT = 500
    CACHE_TTL_SECONDS = 300  # 5 minutes
    
    # Coin name mapping (Symbol => Full Name)
    COIN_NAMES = {
        'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'BNB', 'XRP': 'XRP',
        'SOL': 'Solana', 'ADA': 'Cardano', 'DOGE': 'Dogecoin', 'TRX': 'TRON',
        'DOT': 'Polkadot', 'MATIC': 'Polygon', 'LTC': 'Litecoin', 'SHIB': 'Shiba Inu',
        'AVAX': 'Avalanche', 'LINK': 'Chainlink', 'ATOM': 'Cosmos', 'UNI': 'Uniswap',
        'XMR': 'Monero', 'ETC': 'Ethereum Classic', 'XLM': 'Stellar', 'BCH': 'Bitcoin Cash',
        'FIL': 'Filecoin', 'APT': 'Aptos', 'NEAR': 'NEAR Protocol', 'ARB': 'Arbitrum',
        'OP': 'Optimism', 'VET': 'VeChain', 'ICP': 'Internet Computer', 'HBAR': 'Hedera',
        'MKR': 'Maker', 'AAVE': 'Aave', 'GRT': 'The Graph', 'ALGO': 'Algorand',
        'SAND': 'The Sandbox', 'MANA': 'Decentraland', 'FTM': 'Fantom', 'AXS': 'Axie Infinity',
        'INJ': 'Injective', 'SUI': 'Sui', 'SEI': 'Sei', 'TIA': 'Celestia',
        'PEPE': 'Pepe', 'WIF': 'dogwifhat', 'BONK': 'Bonk', 'FLOKI': 'Floki',
        'RENDER': 'Render', 'FET': 'Fetch.ai', 'TAO': 'Bittensor', 'WLD': 'Worldcoin',
    }
    
    def __init__(self, redis_client=None, cache_dir: str = None):
        """
        Initialize the price aggregator.
        
        Args:
            redis_client: Optional Redis client for caching
            cache_dir: Directory for file-based caching
        """
        self.redis = redis_client
        self.cache_dir = Path(cache_dir) if cache_dir else Path("/tmp/aihub")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def fetch_data(self) -> Dict[str, Any]:
        """
        Main orchestrator method with fallback strategy.
        Order: Binance → OKX → CoinGecko
        
        Returns:
            Dict with success status, source, data, and metadata
        """
        sources = [
            ("Binance", self._get_binance_data),
            ("OKX", self._get_okx_data),
            ("CoinGecko", self._get_coingecko_data),
        ]
        
        last_error = None
        
        for source_name, fetch_func in sources:
            logger.info(f"Attempting to fetch from {source_name}...")
            
            try:
                start_time = datetime.now()
                result = await fetch_func()
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                if result:
                    # Enrich with market data if not from CoinGecko
                    if source_name != "CoinGecko":
                        result = await self._enrich_with_market_cap(result)
                    
                    # Cache the data
                    await self._cache_data(result, source_name)
                    
                    logger.info(f"Successfully fetched {len(result)} coins from {source_name}")
                    
                    return {
                        "success": True,
                        "source": source_name,
                        "coins_count": len(result),
                        "duration_ms": duration_ms,
                        "timestamp": datetime.now().isoformat(),
                        "data": result,
                    }
                    
            except Exception as e:
                logger.warning(f"{source_name} failed: {str(e)}")
                last_error = str(e)
                continue
        
        logger.error("CRITICAL: All API sources failed!")
        return {
            "success": False,
            "error": "All sources failed",
            "last_error": last_error,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def _get_binance_data(self) -> Dict[str, Dict]:
        """
        Fetch data from Binance API.
        Returns dict keyed by symbol.
        """
        session = await self._get_session()
        
        async with session.get(self.BINANCE_TICKER_API) as response:
            if response.status != 200:
                raise Exception(f"Binance API returned {response.status}")
            
            data = await response.json()
        
        # Filter USDT pairs and normalize
        coins = {}
        for ticker in data:
            symbol = ticker.get("symbol", "")
            if not symbol.endswith("USDT"):
                continue
            
            base_symbol = symbol.replace("USDT", "")
            if not base_symbol or len(base_symbol) > 10:
                continue
            
            coins[base_symbol] = {
                "symbol": base_symbol,
                "name": self.COIN_NAMES.get(base_symbol, base_symbol),
                "current_price": float(ticker.get("lastPrice", 0)),
                "price_change_24h": float(ticker.get("priceChange", 0)),
                "price_change_percent_24h": float(ticker.get("priceChangePercent", 0)),
                "high_24h": float(ticker.get("highPrice", 0)),
                "low_24h": float(ticker.get("lowPrice", 0)),
                "volume_24h": float(ticker.get("quoteVolume", 0)),
                "source": "binance",
                "last_updated": datetime.now().isoformat(),
            }
        
        logger.info(f"Binance: Fetched {len(coins)} USDT pairs")
        return coins
    
    async def _get_okx_data(self) -> Dict[str, Dict]:
        """
        Fetch data from OKX API.
        Returns dict keyed by symbol.
        """
        session = await self._get_session()
        
        async with session.get(self.OKX_TICKER_API) as response:
            if response.status != 200:
                raise Exception(f"OKX API returned {response.status}")
            
            result = await response.json()
        
        if result.get("code") != "0":
            raise Exception(f"OKX API error: {result.get('msg', 'Unknown')}")
        
        data = result.get("data", [])
        
        # Filter USDT pairs and normalize
        coins = {}
        for ticker in data:
            inst_id = ticker.get("instId", "")
            if not inst_id.endswith("-USDT"):
                continue
            
            base_symbol = inst_id.replace("-USDT", "")
            if not base_symbol or len(base_symbol) > 10:
                continue
            
            last_price = float(ticker.get("last", 0))
            open_24h = float(ticker.get("open24h", 0))
            change_24h = last_price - open_24h
            change_pct = (change_24h / open_24h * 100) if open_24h else 0
            
            coins[base_symbol] = {
                "symbol": base_symbol,
                "name": self.COIN_NAMES.get(base_symbol, base_symbol),
                "current_price": last_price,
                "price_change_24h": change_24h,
                "price_change_percent_24h": round(change_pct, 2),
                "high_24h": float(ticker.get("high24h", 0)),
                "low_24h": float(ticker.get("low24h", 0)),
                "volume_24h": float(ticker.get("volCcy24h", 0)),
                "source": "okx",
                "last_updated": datetime.now().isoformat(),
            }
        
        logger.info(f"OKX: Fetched {len(coins)} USDT pairs")
        return coins
    
    async def _get_coingecko_data(self) -> Dict[str, Dict]:
        """
        Fetch data from CoinGecko API.
        Returns dict keyed by symbol.
        """
        session = await self._get_session()
        
        all_coins = {}
        per_page = 250
        pages_needed = 2  # 500 coins max
        
        for page in range(1, pages_needed + 1):
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": page,
                "sparkline": "true",
                "price_change_percentage": "1h,24h,7d",
            }
            
            url = f"{self.COINGECKO_MARKETS_API}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            
            async with session.get(url) as response:
                if response.status == 429:
                    logger.warning(f"CoinGecko rate limited on page {page}")
                    break
                if response.status != 200:
                    logger.warning(f"CoinGecko page {page} failed: HTTP {response.status}")
                    continue
                
                data = await response.json()
            
            for coin in data:
                symbol = coin.get("symbol", "").upper()
                if not symbol:
                    continue
                
                all_coins[symbol] = {
                    "coin_id": coin.get("id"),
                    "symbol": symbol,
                    "name": coin.get("name"),
                    "image": coin.get("image"),
                    "current_price": float(coin.get("current_price", 0)),
                    "market_cap": float(coin.get("market_cap", 0)),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_change_percent_24h": float(coin.get("price_change_percentage_24h", 0)),
                    "price_change_percent_1h": float(coin.get("price_change_percentage_1h_in_currency", 0) or 0),
                    "price_change_percent_7d": float(coin.get("price_change_percentage_7d_in_currency", 0) or 0),
                    "high_24h": float(coin.get("high_24h", 0) or 0),
                    "low_24h": float(coin.get("low_24h", 0) or 0),
                    "volume_24h": float(coin.get("total_volume", 0)),
                    "circulating_supply": float(coin.get("circulating_supply", 0) or 0),
                    "total_supply": float(coin.get("total_supply", 0) or 0),
                    "ath": float(coin.get("ath", 0) or 0),
                    "ath_change_percentage": float(coin.get("ath_change_percentage", 0) or 0),
                    "sparkline_7d": coin.get("sparkline_in_7d", {}).get("price"),
                    "source": "coingecko",
                    "last_updated": datetime.now().isoformat(),
                }
            
            logger.info(f"CoinGecko page {page}: {len(data)} coins")
            
            # Small delay to avoid rate limiting
            if page < pages_needed:
                await asyncio.sleep(0.2)
        
        return all_coins
    
    async def _enrich_with_market_cap(self, data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Enrich Binance/OKX data with market cap from CoinGecko.
        """
        try:
            coingecko_data = await self._get_coingecko_data()
            
            enriched_count = 0
            for symbol, coin in data.items():
                if symbol in coingecko_data:
                    cg_coin = coingecko_data[symbol]
                    # Merge CoinGecko fields
                    coin["coin_id"] = cg_coin.get("coin_id")
                    coin["image"] = cg_coin.get("image")
                    coin["market_cap"] = cg_coin.get("market_cap", 0)
                    coin["market_cap_rank"] = cg_coin.get("market_cap_rank")
                    coin["circulating_supply"] = cg_coin.get("circulating_supply")
                    coin["sparkline_7d"] = cg_coin.get("sparkline_7d")
                    if coin["name"] == symbol:
                        coin["name"] = cg_coin.get("name", symbol)
                    enriched_count += 1
            
            logger.info(f"Enriched {enriched_count} coins with CoinGecko data")
            
        except Exception as e:
            logger.warning(f"Failed to enrich with CoinGecko: {e}")
        
        return data
    
    async def _cache_data(self, data: Dict[str, Dict], source: str):
        """Cache data to Redis and/or file."""
        cache_content = {
            "metadata": {
                "source": source,
                "last_updated": datetime.now().isoformat(),
                "total_coins": len(data),
            },
            "data": data,
        }
        
        # Redis cache
        if self.redis:
            try:
                await self.redis.set(
                    "aihub:market_data",
                    json.dumps(cache_content),
                    ex=self.CACHE_TTL_SECONDS
                )
            except Exception as e:
                logger.warning(f"Redis cache failed: {e}")
        
        # File cache (backup)
        cache_file = self.cache_dir / "market_data.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(cache_content, f)
        except Exception as e:
            logger.warning(f"File cache failed: {e}")
    
    async def get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get data from cache (Redis first, then file)."""
        # Try Redis
        if self.redis:
            try:
                cached = await self.redis.get("aihub:market_data")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis read failed: {e}")
        
        # Try file
        cache_file = self.cache_dir / "market_data.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                # Check if stale (older than 10 minutes)
                last_updated = data.get("metadata", {}).get("last_updated")
                if last_updated:
                    updated_dt = datetime.fromisoformat(last_updated)
                    if datetime.now() - updated_dt < timedelta(minutes=10):
                        return data
            except Exception as e:
                logger.warning(f"File cache read failed: {e}")
        
        return None
    
    async def get_market_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get market data, using cache if available.
        
        Args:
            force_refresh: If True, always fetch fresh data
            
        Returns:
            Market data dict
        """
        if not force_refresh:
            cached = await self.get_cached_data()
            if cached:
                return cached
        
        return await self.fetch_data()
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global market statistics from CoinGecko."""
        session = await self._get_session()
        
        try:
            async with session.get(self.COINGECKO_GLOBAL_API) as response:
                if response.status != 200:
                    raise Exception(f"CoinGecko global API returned {response.status}")
                
                data = await response.json()
                global_data = data.get("data", {})
                
                return {
                    "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                    "total_volume_24h": global_data.get("total_volume", {}).get("usd", 0),
                    "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                    "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                    "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                    "markets": global_data.get("markets", 0),
                    "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd", 0),
                    "last_updated": datetime.now().isoformat(),
                }
                
        except Exception as e:
            logger.error(f"Failed to get global stats: {e}")
            return {}


# Singleton instance
_price_aggregator: Optional[PriceAggregator] = None


def get_price_aggregator(redis_client=None) -> PriceAggregator:
    """Get or create singleton PriceAggregator instance."""
    global _price_aggregator
    if _price_aggregator is None:
        _price_aggregator = PriceAggregator(redis_client=redis_client)
    return _price_aggregator
