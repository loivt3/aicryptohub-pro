"""
On-Chain Data Collector Service for AI Hub - OPTIMIZED VERSION
Production-grade, high-accuracy signal engine using FREE APIs (Etherscan/BscScan)

FEATURES:
- Dynamic chain configuration with block times
- Built-in exchange addresses with DB fallback
- Exponential backoff retry for rate limits
- Smart money filtering (exclude bridges/exchanges)
- Historical data seeding for cold start
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from decimal import Decimal
import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Etherscan V2 unified endpoint
ETHERSCAN_V2_BASE = "https://api.etherscan.io/v2/api"

# Chain-specific configuration
CHAIN_CONFIG = {
    1:     {'slug': 'ethereum',  'block_time': 12,   'whale_threshold': 100000, 'native_decimals': 18},
    56:    {'slug': 'bsc',       'block_time': 3,    'whale_threshold': 50000,  'native_decimals': 18},
    137:   {'slug': 'polygon',   'block_time': 2,    'whale_threshold': 25000,  'native_decimals': 18},
    42161: {'slug': 'arbitrum',  'block_time': 0.26, 'whale_threshold': 50000,  'native_decimals': 18},
    10:    {'slug': 'optimism',  'block_time': 2,    'whale_threshold': 30000,  'native_decimals': 18},
    43114: {'slug': 'avalanche', 'block_time': 2,    'whale_threshold': 30000,  'native_decimals': 18},
    8453:  {'slug': 'base',      'block_time': 2,    'whale_threshold': 30000,  'native_decimals': 18},
    250:   {'slug': 'fantom',    'block_time': 1,    'whale_threshold': 20000,  'native_decimals': 18},
    25:    {'slug': 'cronos',    'block_time': 5.8,  'whale_threshold': 20000,  'native_decimals': 18},
    324:   {'slug': 'zksync',    'block_time': 1,    'whale_threshold': 30000,  'native_decimals': 18},
}

# Built-in known exchange hot wallet addresses (fallback when DB is empty)
KNOWN_EXCHANGES = {
    # Binance Hot Wallets
    '0x28c6c06298d514db089934071355e5743bf21d60': {'label': 'Binance Hot 14', 'exchange': 'Binance', 'is_deposit': False},
    '0x21a31ee1afc51d94c2efccaa2092ad1028285549': {'label': 'Binance 20', 'exchange': 'Binance', 'is_deposit': False},
    '0xdfd5293d8e347dfe59e90efd55b2956a1343963d': {'label': 'Binance 8', 'exchange': 'Binance', 'is_deposit': False},
    '0x56eddb7aa87536c09ccc2793473599fd21a8b17f': {'label': 'Binance 16', 'exchange': 'Binance', 'is_deposit': False},
    '0x9696f59e4d72e237be84ffd425dcad154bf96976': {'label': 'Binance 18', 'exchange': 'Binance', 'is_deposit': False},
    
    # Coinbase
    '0x503828976d22510aad0201ac7ec88293211d23da': {'label': 'Coinbase 2', 'exchange': 'Coinbase', 'is_deposit': False},
    '0x71660c4005ba85c37ccec55d0c4493e66fe775d3': {'label': 'Coinbase 3', 'exchange': 'Coinbase', 'is_deposit': False},
    '0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740': {'label': 'Coinbase 4', 'exchange': 'Coinbase', 'is_deposit': False},
    
    # OKX (OKEx)
    '0x6cc5f688a315f3dc28a7781717a9a798a59fda7b': {'label': 'OKX', 'exchange': 'OKX', 'is_deposit': False},
    '0x236f9f97e0e62388479bf9e5ba4889e46b0273c3': {'label': 'OKX 2', 'exchange': 'OKX', 'is_deposit': False},
    '0xa7efae728d2936e78bda97dc267687568dd593f3': {'label': 'OKX 3', 'exchange': 'OKX', 'is_deposit': False},
    
    # Kraken
    '0x2910543af39aba0cd09dbb2d50200b3e800a63d2': {'label': 'Kraken 4', 'exchange': 'Kraken', 'is_deposit': False},
    '0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13': {'label': 'Kraken 6', 'exchange': 'Kraken', 'is_deposit': False},
    
    # Bybit
    '0xf89d7b9c864f589bbf53a82105107622b35eaa40': {'label': 'Bybit', 'exchange': 'Bybit', 'is_deposit': False},
    '0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4': {'label': 'Bybit 2', 'exchange': 'Bybit', 'is_deposit': False},
    
    # KuCoin
    '0x2b5634c42055806a59e9107ed44d43c426e58258': {'label': 'KuCoin', 'exchange': 'KuCoin', 'is_deposit': False},
    '0x689c56aef474df92d44a1b70850f808488f9769c': {'label': 'KuCoin 2', 'exchange': 'KuCoin', 'is_deposit': False},
    
    # Huobi/HTX
    '0x5401dbf7da53e1c9dbf484e3d69505815f2f5e6e': {'label': 'HTX', 'exchange': 'HTX', 'is_deposit': False},
    '0xecd0d12e21805553f6287c3d8e28dc27e8e37a8a': {'label': 'HTX 2', 'exchange': 'HTX', 'is_deposit': False},
    
    # Gate.io
    '0x0d0707963952f2fba59dd06f2b425ace40b492fe': {'label': 'Gate.io', 'exchange': 'Gate.io', 'is_deposit': False},
    '0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c': {'label': 'Gate.io 2', 'exchange': 'Gate.io', 'is_deposit': False},
}

# Null/burn addresses to exclude
NULL_ADDRESSES = {
    '0x0000000000000000000000000000000000000000',
    '0x000000000000000000000000000000000000dead',
    '0xdead000000000000000000000000000000000000',
}

# Known bridge/protocol addresses to exclude from "smart money"
KNOWN_BRIDGES = {
    '0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf': 'Polygon Bridge',
    '0xa3a7b6f88361f48403514059f1f16c8e78d60eec': 'Arbitrum Bridge',
    '0x99c9fc46f92e8a1c0dec1b1747d010903e884be1': 'Optimism Bridge',
}

# Known staking contracts to exclude
KNOWN_STAKING = {
    '0x00000000219ab540356cbb839cbe05303d7705fa': 'ETH 2.0 Deposit Contract',
}

# Runtime storage for exchange addresses (DB + fallback merged)
EXCHANGE_ADDRESSES: Dict[str, Dict] = {}


class OnChainCollector:
    """
    Production-grade collector service for on-chain data:
    - Whale transactions (>$100K)
    - Daily Active Addresses (DAU)
    - Top holder tracking (filtered for smart money only)
    """
    
    REQUEST_DELAY = 0.25  # 4 requests/sec for Etherscan free tier
    MAX_RETRIES = 3       # Retry with exponential backoff
    
    def __init__(self, db_service, api_key: str = None):
        """
        Initialize collector with database service and API key
        
        Args:
            db_service: DatabaseService instance for PostgreSQL
            api_key: Etherscan API key
        """
        self.db = db_service
        self.api_key = api_key or ""
        self._last_request = 0
        self._client = None
        self._contract_cache: Dict[str, bool] = {}  # Cache for is_contract checks
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
        
    async def _rate_limit(self):
        """Enforce rate limiting"""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self._last_request = asyncio.get_event_loop().time()
        
    async def _etherscan_request(
        self,
        chain_id: int,
        params: Dict[str, Any],
        max_retries: int = None,
    ) -> Optional[Dict]:
        """
        Make request to Etherscan V2 unified API with exponential backoff retry
        
        Args:
            chain_id: Chain ID (1 for ETH, 56 for BSC, etc.)
            params: API parameters
            max_retries: Override default max retries
            
        Returns:
            API response or None on error
        """
        retries = max_retries or self.MAX_RETRIES
        
        for attempt in range(retries):
            await self._rate_limit()
            
            try:
                client = await self._get_client()
                
                # Build params with chainid and apikey
                params["chainid"] = chain_id
                params["apikey"] = self.api_key
                
                url = ETHERSCAN_V2_BASE
                response = await client.get(url, params=params)
                
                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{retries})")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # Handle server errors with retry
                if response.status_code >= 500:
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error {response.status_code}, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                # Check for success
                if data.get("status") == "1":
                    return data
                elif data.get("result") and isinstance(data.get("result"), list):
                    return data
                else:
                    error_msg = data.get("message") or data.get("result") or "Unknown error"
                    # Don't retry on "No transactions found" type errors
                    if "No transactions" in str(error_msg) or "No records" in str(error_msg):
                        return data  # Return empty result, not error
                    logger.warning(f"Etherscan error for chain {chain_id}: {error_msg}")
                    return None
                    
            except httpx.TimeoutException:
                wait_time = 2 ** attempt
                logger.warning(f"Timeout, waiting {wait_time}s (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(wait_time)
                continue
                
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Etherscan request failed after {retries} attempts: {e}")
                    
        return None
        
    async def load_exchange_addresses(self):
        """Load known exchange addresses from database and merge with built-in fallback"""
        global EXCHANGE_ADDRESSES
        
        # Start with built-in addresses as fallback
        EXCHANGE_ADDRESSES = {k.lower(): v for k, v in KNOWN_EXCHANGES.items()}
        
        try:
            query = """
                SELECT address, chain_slug, label, exchange_name, is_deposit
                FROM known_addresses
                WHERE address_type = 'exchange'
            """
            rows = await self.db.fetch_all(query)
            
            # Merge DB addresses (DB takes precedence)
            for row in rows:
                addr = row['address'].lower()
                EXCHANGE_ADDRESSES[addr] = {
                    'label': row['label'],
                    'exchange': row['exchange_name'],
                    'is_deposit': row['is_deposit'],
                }
                
            logger.info(f"Loaded {len(EXCHANGE_ADDRESSES)} known exchange addresses (DB + fallback)")
            
        except Exception as e:
            logger.warning(f"Failed to load DB exchange addresses (using fallback): {e}")
            logger.info(f"Using {len(EXCHANGE_ADDRESSES)} built-in exchange addresses")
            
    def _is_exchange_address(self, address: str) -> Optional[Dict]:
        """Check if address is a known exchange wallet"""
        return EXCHANGE_ADDRESSES.get(address.lower())
        
    def _is_excluded_address(self, address: str, contract_address: str = None) -> bool:
        """Check if address should be excluded from smart money analysis"""
        addr = address.lower()
        
        # Null/burn addresses
        if addr in NULL_ADDRESSES:
            return True
            
        # Contract itself
        if contract_address and addr == contract_address.lower():
            return True
            
        # Exchange addresses
        if self._is_exchange_address(addr):
            return True
            
        # Known bridges
        if addr in KNOWN_BRIDGES:
            return True
            
        # Known staking contracts
        if addr in KNOWN_STAKING:
            return True
            
        return False
        
    async def _is_contract(self, chain_id: int, address: str) -> bool:
        """
        Check if address is a contract using Etherscan getcode API
        
        Args:
            chain_id: Chain ID
            address: Address to check
            
        Returns:
            True if address is a contract
        """
        addr = address.lower()
        
        # Check cache first
        cache_key = f"{chain_id}:{addr}"
        if cache_key in self._contract_cache:
            return self._contract_cache[cache_key]
            
        try:
            params = {
                "module": "proxy",
                "action": "eth_getCode",
                "address": address,
                "tag": "latest",
            }
            
            response = await self._etherscan_request(chain_id, params, max_retries=1)
            
            if response and response.get("result"):
                code = response["result"]
                is_contract = code != "0x" and len(code) > 2
                self._contract_cache[cache_key] = is_contract
                return is_contract
                
        except Exception as e:
            logger.debug(f"Failed to check if {address} is contract: {e}")
            
        return False
        
    def _get_blocks_per_hour(self, chain_id: int) -> int:
        """Calculate blocks per hour for a specific chain"""
        config = CHAIN_CONFIG.get(chain_id, {'block_time': 12})
        block_time = config['block_time']
        return int(3600 / block_time)
        
    def _get_whale_threshold(self, chain_id: int) -> int:
        """Get whale threshold for a specific chain"""
        config = CHAIN_CONFIG.get(chain_id, {'whale_threshold': 100000})
        return config['whale_threshold']
        
    async def collect_whale_transactions(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        contract_address: str,
        token_price_usd: float,
        token_decimals: int = 18,
        hours_back: int = 24,
    ) -> List[Dict]:
        """
        Collect whale transactions (>threshold) for a token
        
        Uses Etherscan tokentx API to get ERC20 transfers
        Filters by USD value threshold (dynamic per chain)
        
        Args:
            coin_id: Coin identifier (e.g., 'ethereum')
            chain_slug: Chain slug (e.g., 'ethereum')
            chain_id: Chain ID (e.g., 1)
            contract_address: Token contract address
            token_price_usd: Current token price in USD
            token_decimals: Token decimals (default 18)
            hours_back: Hours to look back (default 24)
            
        Returns:
            List of whale transactions
        """
        whale_txs = []
        whale_threshold = self._get_whale_threshold(chain_id)
        
        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": contract_address,
                "page": 1,
                "offset": 100,  # Max per page
                "sort": "desc",
            }
            
            response = await self._etherscan_request(chain_id, params)
            
            if not response or not response.get("result"):
                return whale_txs
                
            cutoff_timestamp = datetime.utcnow() - timedelta(hours=hours_back)
            
            for tx in response.get("result", []):
                # Parse timestamp
                tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                
                if tx_time < cutoff_timestamp:
                    break  # Stop if older than cutoff
                    
                # Calculate value in USD
                raw_value = int(tx.get("value", 0))
                token_value = raw_value / (10 ** token_decimals)
                usd_value = token_value * token_price_usd
                
                # Filter by whale threshold (dynamic per chain)
                if usd_value >= whale_threshold:
                    from_addr = tx.get("from", "").lower()
                    to_addr = tx.get("to", "").lower()
                    
                    # Classify transaction
                    from_exchange = self._is_exchange_address(from_addr)
                    to_exchange = self._is_exchange_address(to_addr)
                    
                    if to_exchange:
                        tx_type = "exchange_deposit"
                        exchange_name = to_exchange.get("exchange")
                    elif from_exchange:
                        tx_type = "exchange_withdraw"
                        exchange_name = from_exchange.get("exchange")
                    else:
                        tx_type = "transfer"
                        exchange_name = None
                        
                    whale_tx = {
                        "coin_id": coin_id,
                        "chain_slug": chain_slug,
                        "tx_hash": tx.get("hash"),
                        "from_address": from_addr,
                        "to_address": to_addr,
                        "value_usd": round(usd_value, 2),
                        "value_native": token_value,
                        "tx_type": tx_type,
                        "is_exchange_related": bool(from_exchange or to_exchange),
                        "exchange_name": exchange_name,
                        "block_number": int(tx.get("blockNumber", 0)),
                        "tx_timestamp": tx_time,
                    }
                    
                    whale_txs.append(whale_tx)
                    
            logger.info(f"Found {len(whale_txs)} whale transactions for {coin_id} (threshold: ${whale_threshold:,})")
            
        except Exception as e:
            logger.error(f"Failed to collect whale txs for {coin_id}: {e}")
            
        return whale_txs
        
    async def collect_native_whale_transactions(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        native_price_usd: float,
        hours_back: int = 24,
    ) -> List[Dict]:
        """
        Collect whale transactions for native tokens (ETH, BNB, etc.)
        using txlist API instead of tokentx
        
        Args:
            coin_id: Coin identifier (e.g., 'ethereum', 'binancecoin')
            chain_slug: Chain slug (e.g., 'ethereum', 'bsc')
            chain_id: Chain ID (e.g., 1, 56)
            native_price_usd: Current native token price in USD
            hours_back: Hours to look back (default 24)
            
        Returns:
            List of whale transactions
        """
        whale_txs = []
        whale_threshold = self._get_whale_threshold(chain_id)
        
        if not self.api_key or native_price_usd <= 0:
            logger.warning(f"Cannot collect native whale txs: missing API key or price")
            return whale_txs
            
        try:
            # For native tokens, we look at large transfers to/from known exchange addresses
            exchange_addrs = list(EXCHANGE_ADDRESSES.keys())[:10]  # Top 10 exchanges
            
            cutoff_timestamp = datetime.utcnow() - timedelta(hours=hours_back)
            
            for exchange_addr in exchange_addrs:
                if not exchange_addr:
                    continue
                    
                params = {
                    "module": "account",
                    "action": "txlist",
                    "address": exchange_addr,
                    "page": 1,
                    "offset": 50,
                    "sort": "desc",
                }
                
                response = await self._etherscan_request(chain_id, params)
                
                if not response or not response.get("result"):
                    continue
                    
                for tx in response.get("result", []):
                    # Skip failed transactions
                    if tx.get("isError") == "1":
                        continue
                        
                    tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                    
                    if tx_time < cutoff_timestamp:
                        break
                        
                    # Calculate value in USD
                    raw_value = int(tx.get("value", 0))
                    native_value = raw_value / (10 ** 18)
                    usd_value = native_value * native_price_usd
                    
                    if usd_value >= whale_threshold:
                        from_addr = tx.get("from", "").lower()
                        to_addr = tx.get("to", "").lower()
                        
                        from_exchange = self._is_exchange_address(from_addr)
                        to_exchange = self._is_exchange_address(to_addr)
                        
                        if to_exchange:
                            tx_type = "exchange_deposit"
                            exchange_name = to_exchange.get("exchange")
                        elif from_exchange:
                            tx_type = "exchange_withdraw"
                            exchange_name = from_exchange.get("exchange")
                        else:
                            tx_type = "transfer"
                            exchange_name = None
                            
                        whale_tx = {
                            "coin_id": coin_id,
                            "chain_slug": chain_slug,
                            "tx_hash": tx.get("hash"),
                            "from_address": from_addr,
                            "to_address": to_addr,
                            "value_usd": round(usd_value, 2),
                            "value_native": native_value,
                            "tx_type": tx_type,
                            "is_exchange_related": True,
                            "exchange_name": exchange_name,
                            "block_number": int(tx.get("blockNumber", 0)),
                            "tx_timestamp": tx_time,
                        }
                        
                        # Avoid duplicates
                        if not any(w["tx_hash"] == whale_tx["tx_hash"] for w in whale_txs):
                            whale_txs.append(whale_tx)
                            
            logger.info(f"Found {len(whale_txs)} native whale transactions for {coin_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect native whale txs for {coin_id}: {e}")
            
        return whale_txs
        
    async def save_whale_transactions(self, transactions: List[Dict]) -> int:
        """
        Save whale transactions to database
        
        Args:
            transactions: List of whale transaction dicts
            
        Returns:
            Number of transactions saved
        """
        if not transactions:
            return 0
            
        saved = 0
        
        for tx in transactions:
            try:
                query = """
                    INSERT INTO whale_transactions (
                        coin_id, chain_slug, tx_hash, from_address, to_address,
                        value_usd, value_native, tx_type, is_exchange_related,
                        exchange_name, block_number, tx_timestamp
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                    )
                    ON CONFLICT (tx_hash) DO NOTHING
                """
                
                await self.db.execute(
                    query,
                    tx["coin_id"], tx["chain_slug"], tx["tx_hash"],
                    tx["from_address"], tx["to_address"],
                    tx["value_usd"], tx["value_native"], tx["tx_type"],
                    tx["is_exchange_related"], tx["exchange_name"],
                    tx["block_number"], tx["tx_timestamp"]
                )
                saved += 1
                
            except Exception as e:
                logger.warning(f"Failed to save tx {tx.get('tx_hash')}: {e}")
                
        return saved
    
    # =========================================================================
    # TOP HOLDER COLLECTION (The Graph + Whale Pattern Analysis)
    # =========================================================================
    
    # The Graph public subgraph endpoints (free, decentralized)
    GRAPH_ENDPOINTS = {
        "uniswap": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        "aave": "https://api.thegraph.com/subgraphs/name/aave/protocol-v3",
    }
    
    async def collect_top_holders(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        contract_address: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Collect top holders using multiple strategies:
        1. Whale transaction pattern analysis (primary - uses existing data)
        2. The Graph (for tokens with public subgraphs)
        """
        holders = []
        
        # Strategy 1: Estimate from whale transaction patterns (most reliable)
        holders = await self._estimate_holders_from_whales(coin_id, limit)
        if holders:
            logger.info(f"Estimated {len(holders)} holders from whale patterns for {coin_id}")
            await self._save_holder_snapshot(coin_id, chain_slug, holders)
            return holders
        
        logger.debug(f"No holder data for {coin_id}")
        return []
    
    async def _estimate_holders_from_whales(
        self,
        coin_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Estimate top holders by analyzing whale transaction patterns.
        Addresses with net positive flow (accumulating) are likely top holders.
        """
        from sqlalchemy import text
        
        query = text("""
            WITH address_flows AS (
                SELECT 
                    to_address as address,
                    SUM(value_usd) as inflow,
                    0::numeric as outflow
                FROM whale_transactions
                WHERE coin_id = :coin_id
                  AND tx_timestamp > NOW() - INTERVAL '30 days'
                GROUP BY to_address
                
                UNION ALL
                
                SELECT 
                    from_address as address,
                    0::numeric as inflow,
                    SUM(value_usd) as outflow
                FROM whale_transactions
                WHERE coin_id = :coin_id
                  AND tx_timestamp > NOW() - INTERVAL '30 days'
                GROUP BY from_address
            ),
            net_positions AS (
                SELECT 
                    address,
                    SUM(inflow) as total_inflow,
                    SUM(outflow) as total_outflow,
                    SUM(inflow) - SUM(outflow) as net_position
                FROM address_flows
                WHERE address NOT IN (
                    '0x0000000000000000000000000000000000000000',
                    '0x000000000000000000000000000000000000dead'
                )
                GROUP BY address
                HAVING SUM(inflow) - SUM(outflow) > 0
            )
            SELECT address, total_inflow, total_outflow, net_position
            FROM net_positions
            ORDER BY net_position DESC
            LIMIT :limit
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id, "limit": limit})
                rows = result.fetchall()
                
                if not rows:
                    return []
                
                total_net = sum(float(row[3]) for row in rows)
                
                holders = []
                for row in rows:
                    pct = (float(row[3]) / total_net * 100) if total_net > 0 else 0
                    holders.append({
                        "address": row[0],
                        "balance": float(row[3]),
                        "percentage": round(pct, 2),
                        "is_accumulating": float(row[1]) > float(row[2]),
                    })
                
                return holders
                
        except Exception as e:
            logger.debug(f"Whale-based holder estimation failed for {coin_id}: {e}")
            return []
    
    async def _save_holder_snapshot(
        self, coin_id: str, chain_slug: str, holders: List[Dict]
    ) -> bool:
        """Save holder snapshot to database"""
        from sqlalchemy import text
        from datetime import date
        
        if not holders:
            return False
        
        top10 = holders[:10] if len(holders) >= 10 else holders
        top10_total_pct = sum(h.get("percentage", 0) for h in top10)
        
        query = text("""
            INSERT INTO top_holder_snapshots (
                coin_id, chain_slug, snapshot_date, 
                top10_total_balance, top10_pct_of_supply
            ) VALUES (:coin_id, :chain_slug, :snapshot_date, :top10_balance, :top10_pct)
            ON CONFLICT (coin_id, snapshot_date) DO UPDATE SET
                top10_total_balance = EXCLUDED.top10_total_balance,
                top10_pct_of_supply = EXCLUDED.top10_pct_of_supply
        """)
        
        try:
            with self.db.engine.begin() as conn:
                conn.execute(query, {
                    "coin_id": coin_id,
                    "chain_slug": chain_slug,
                    "snapshot_date": date.today(),
                    "top10_balance": sum(h.get("balance", 0) for h in top10),
                    "top10_pct": top10_total_pct,
                })
            return True
        except Exception as e:
            logger.debug(f"Failed to save holder snapshot for {coin_id}: {e}")
            return False
        
    async def calculate_whale_signals(
        self,
        coin_id: str,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Calculate whale activity signals from stored transactions
        
        Args:
            coin_id: Coin identifier
            hours: Hours to analyze (default 24)
            
        Returns:
            Dict with whale signals
        """
        try:
            query_current = """
                SELECT 
                    COUNT(*) as tx_count,
                    COALESCE(SUM(CASE WHEN tx_type = 'exchange_deposit' THEN value_usd ELSE 0 END), 0) as inflow,
                    COALESCE(SUM(CASE WHEN tx_type = 'exchange_withdraw' THEN value_usd ELSE 0 END), 0) as outflow
                FROM whale_transactions
                WHERE coin_id = $1
                AND tx_timestamp >= NOW() - INTERVAL '%s hours'
            """ % hours
            
            current = await self.db.fetch_one(query_current, coin_id)
            
            query_prev = """
                SELECT COUNT(*) as tx_count
                FROM whale_transactions
                WHERE coin_id = $1
                AND tx_timestamp >= NOW() - INTERVAL '%s hours'
                AND tx_timestamp < NOW() - INTERVAL '%s hours'
            """ % (hours * 2, hours)
            
            prev = await self.db.fetch_one(query_prev, coin_id)
            
            tx_count_current = current['tx_count'] if current else 0
            tx_count_prev = prev['tx_count'] if prev else 0
            inflow = float(current['inflow']) if current else 0
            outflow = float(current['outflow']) if current else 0
            net_flow = inflow - outflow
            
            # Calculate change percentage
            if tx_count_prev > 0:
                change_pct = ((tx_count_current - tx_count_prev) / tx_count_prev) * 100
            else:
                change_pct = 100 if tx_count_current > 0 else 0
                
            # Determine signal
            if net_flow < -500000:  # >$500K net outflow
                signal = "BULLISH"
            elif net_flow > 500000:  # >$500K net inflow
                signal = "BEARISH"
            elif change_pct > 100:  # Spike in whale activity
                signal = "VOLATILE"
            else:
                signal = "NEUTRAL"
                
            return {
                "whale_tx_count_24h": tx_count_current,
                "whale_tx_count_prev_24h": tx_count_prev,
                "whale_tx_change_pct": round(change_pct, 2),
                "whale_inflow_usd": inflow,
                "whale_outflow_usd": outflow,
                "whale_net_flow_usd": net_flow,
                "whale_signal": signal,
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate whale signals for {coin_id}: {e}")
            return {
                "whale_tx_count_24h": 0,
                "whale_tx_change_pct": 0,
                "whale_signal": "NEUTRAL",
            }
            
    async def collect_daily_active_addresses(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        contract_address: str,
    ) -> Dict[str, Any]:
        """
        Estimate Daily Active Addresses from transaction count
        
        Note: Etherscan free tier doesn't provide direct DAU.
        We estimate from unique addresses in recent transactions.
        
        Args:
            coin_id: Coin identifier
            chain_slug: Chain slug
            chain_id: Chain ID
            contract_address: Token contract address
            
        Returns:
            DAU metrics dict
        """
        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": contract_address,
                "page": 1,
                "offset": 100,
                "sort": "desc",
            }
            
            response = await self._etherscan_request(chain_id, params)
            
            if not response or not response.get("result"):
                return {"active_addresses": 0, "tx_count": 0}
                
            today = datetime.utcnow().date()
            
            unique_addresses = set()
            tx_count = 0
            
            for tx in response.get("result", []):
                tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                
                if tx_time.date() == today:
                    unique_addresses.add(tx.get("from", "").lower())
                    unique_addresses.add(tx.get("to", "").lower())
                    tx_count += 1
                    
            # Remove empty addresses
            unique_addresses.discard("")
            
            dau_data = {
                "coin_id": coin_id,
                "chain_slug": chain_slug,
                "date": today,
                "active_addresses": len(unique_addresses),
                "tx_count": tx_count,
            }
            
            await self._save_dau_snapshot(dau_data)
            
            return dau_data
            
        except Exception as e:
            logger.error(f"Failed to collect DAU for {coin_id}: {e}")
            return {"active_addresses": 0, "tx_count": 0}
            
    async def _save_dau_snapshot(self, dau_data: Dict):
        """Save DAU snapshot to database"""
        try:
            query = """
                INSERT INTO daily_active_addresses (
                    coin_id, chain_slug, date, active_addresses, tx_count
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (coin_id, chain_slug, date) 
                DO UPDATE SET 
                    active_addresses = EXCLUDED.active_addresses,
                    tx_count = EXCLUDED.tx_count
            """
            
            await self.db.execute(
                query,
                dau_data["coin_id"], dau_data["chain_slug"],
                dau_data["date"], dau_data["active_addresses"],
                dau_data["tx_count"]
            )
            
        except Exception as e:
            logger.error(f"Failed to save DAU snapshot: {e}")
            
    async def calculate_dau_signals(
        self,
        coin_id: str,
    ) -> Dict[str, Any]:
        """
        Calculate DAU trend signals from stored snapshots
        
        Args:
            coin_id: Coin identifier
            
        Returns:
            DAU signals dict
        """
        try:
            query = """
                SELECT date, active_addresses
                FROM daily_active_addresses
                WHERE coin_id = $1
                ORDER BY date DESC
                LIMIT 7
            """
            
            rows = await self.db.fetch_all(query, coin_id)
            
            if not rows or len(rows) < 2:
                return {
                    "dau_current": 0,
                    "dau_change_1d_pct": 0,
                    "dau_change_3d_pct": 0,
                    "dau_change_7d_pct": 0,
                    "dau_trend": "STABLE",
                    "network_signal": "NEUTRAL",
                }
                
            dau_current = rows[0]['active_addresses']
            dau_prev_day = rows[1]['active_addresses'] if len(rows) > 1 else dau_current
            dau_3d_ago = rows[2]['active_addresses'] if len(rows) > 2 else dau_current
            dau_7d_ago = rows[-1]['active_addresses'] if len(rows) >= 7 else dau_current
            
            def calc_change(current, prev):
                if prev > 0:
                    return ((current - prev) / prev) * 100
                return 0
                
            change_1d = calc_change(dau_current, dau_prev_day)
            change_3d = calc_change(dau_current, dau_3d_ago)
            change_7d = calc_change(dau_current, dau_7d_ago)
            
            dau_avg_7d = sum(r['active_addresses'] for r in rows) / len(rows)
            
            if change_3d > 10:
                trend = "GROWING"
                signal = "BULLISH"
            elif change_3d < -10:
                trend = "DECLINING"
                signal = "BEARISH"
            else:
                trend = "STABLE"
                signal = "NEUTRAL"
                
            return {
                "dau_current": dau_current,
                "dau_prev_day": dau_prev_day,
                "dau_avg_7d": int(dau_avg_7d),
                "dau_change_1d_pct": round(change_1d, 2),
                "dau_change_3d_pct": round(change_3d, 2),
                "dau_change_7d_pct": round(change_7d, 2),
                "dau_trend": trend,
                "network_signal": signal,
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate DAU signals for {coin_id}: {e}")
            return {
                "dau_current": 0,
                "dau_trend": "STABLE",
                "network_signal": "NEUTRAL",
            }
            
    async def collect_top_holders(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        contract_address: str,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Collect top token holders using Etherscan token holder API
        FILTERED: Excludes exchanges, bridges, null addresses (smart money only)
        
        Args:
            coin_id: Coin identifier
            chain_slug: Chain slug
            chain_id: Chain ID
            contract_address: Token contract
            limit: Number of holders to fetch
            
        Returns:
            List of top holders (smart money only)
        """
        try:
            params = {
                "module": "token",
                "action": "tokenholderlist",
                "contractaddress": contract_address,
                "page": 1,
                "offset": min(limit * 2, 200),  # Fetch extra to account for filtered addresses
            }
            
            response = await self._etherscan_request(chain_id, params)
            
            if not response or not response.get("result"):
                logger.warning(f"No holder data for {coin_id}")
                return []
                
            holders = []
            rank = 1
            
            for holder in response.get("result", []):
                addr = holder.get("TokenHolderAddress", "").lower()
                
                # SMART MONEY FILTER: Skip excluded addresses
                if self._is_excluded_address(addr, contract_address):
                    continue
                    
                holders.append({
                    "rank": rank,
                    "address": addr,
                    "balance": holder.get("TokenHolderQuantity", "0"),
                    "pct": 0,  # Would need total supply calculation
                })
                rank += 1
                
                if rank > limit:
                    break
                    
            logger.info(f"Found {len(holders)} smart money holders for {coin_id} (filtered from {len(response.get('result', []))})")
            return holders
            
        except Exception as e:
            logger.error(f"Failed to collect top holders for {coin_id}: {e}")
            return []
            
    async def calculate_holder_signals(
        self,
        coin_id: str,
    ) -> Dict[str, Any]:
        """
        Calculate top holder accumulation signals
        
        Args:
            coin_id: Coin identifier
            
        Returns:
            Holder signals dict
        """
        try:
            query = """
                SELECT snapshot_date, top10_total_balance, top10_pct_of_supply
                FROM top_holder_snapshots
                WHERE coin_id = $1
                ORDER BY snapshot_date DESC
                LIMIT 7
            """
            
            rows = await self.db.fetch_all(query, coin_id)
            
            if not rows or len(rows) < 2:
                return {
                    "top10_change_pct": 0,
                    "accumulation_score": 50,
                    "holder_signal": "NEUTRAL",
                }
                
            current = float(rows[0]['top10_total_balance'] or 0)
            prev_7d = float(rows[-1]['top10_total_balance'] or 0)
            
            if prev_7d > 0:
                change_pct = ((current - prev_7d) / prev_7d) * 100
            else:
                change_pct = 0
                
            if change_pct > 5:
                score = min(100, 80 + change_pct)
                signal = "BULLISH"
            elif change_pct < -5:
                score = max(0, 20 + change_pct)
                signal = "BEARISH"
            else:
                score = 50 + (change_pct * 4)
                signal = "NEUTRAL"
                
            return {
                "top10_balance_current": current,
                "top10_balance_prev_7d": prev_7d,
                "top10_change_pct": round(change_pct, 2),
                "accumulation_score": round(score, 2),
                "holder_signal": signal,
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate holder signals for {coin_id}: {e}")
            return {
                "top10_change_pct": 0,
                "accumulation_score": 50,
                "holder_signal": "NEUTRAL",
            }
            
    async def calculate_overall_signal(
        self,
        whale_signals: Dict,
        dau_signals: Dict,
        holder_signals: Dict,
    ) -> Dict[str, Any]:
        """
        Calculate overall on-chain signal from components
        
        Args:
            whale_signals: Whale activity signals
            dau_signals: DAU/network signals
            holder_signals: Top holder signals
            
        Returns:
            Overall signal dict
        """
        signals = []
        weights = []
        
        # Whale signal (weight 3)
        whale = whale_signals.get("whale_signal", "NEUTRAL")
        if whale == "BULLISH":
            signals.append(1)
        elif whale == "BEARISH":
            signals.append(-1)
        else:
            signals.append(0)
        weights.append(3)
        
        # Network signal (weight 2)
        network = dau_signals.get("network_signal", "NEUTRAL")
        if network == "BULLISH":
            signals.append(1)
        elif network == "BEARISH":
            signals.append(-1)
        else:
            signals.append(0)
        weights.append(2)
        
        # Holder signal (weight 2)
        holder = holder_signals.get("holder_signal", "NEUTRAL")
        if holder == "BULLISH":
            signals.append(1)
        elif holder == "BEARISH":
            signals.append(-1)
        else:
            signals.append(0)
        weights.append(2)
        
        # Calculate weighted score
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(signals, weights))
        score = weighted_sum / total_weight
        
        # Convert to probability (0-100%)
        bullish_prob = (score + 1) * 50
        
        if score > 0.3:
            overall = "BULLISH"
        elif score < -0.3:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"
            
        return {
            "overall_signal": overall,
            "bullish_probability": round(bullish_prob, 2),
            "confidence_score": round(abs(score) * 100, 2),
        }
        
    async def seed_historical_data(
        self,
        coin_id: str,
        chain_slug: str,
        chain_id: int,
        contract_address: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Seed historical data for a new coin to solve cold start problem
        
        This creates 7 days of estimated DAU snapshots based on available data,
        ensuring the dashboard shows trends immediately
        
        Args:
            coin_id: Coin identifier
            chain_slug: Chain slug
            chain_id: Chain ID
            contract_address: Token contract address
            days: Number of days to backfill (default 7)
            
        Returns:
            Summary of seeded data
        """
        logger.info(f"Seeding {days} days of historical data for {coin_id}")
        
        seeded = {
            "coin_id": coin_id,
            "days_seeded": 0,
            "dau_snapshots": [],
        }
        
        try:
            # Get recent transactions to estimate historical activity
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": contract_address,
                "page": 1,
                "offset": 1000,  # Fetch more for historical estimation
                "sort": "desc",
            }
            
            response = await self._etherscan_request(chain_id, params)
            
            if not response or not response.get("result"):
                logger.warning(f"No transaction data for seeding {coin_id}")
                return seeded
                
            txs = response.get("result", [])
            
            # Group transactions by date
            daily_addresses: Dict[str, Set[str]] = {}
            daily_tx_count: Dict[str, int] = {}
            
            for tx in txs:
                tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                date_str = tx_time.date().isoformat()
                
                if date_str not in daily_addresses:
                    daily_addresses[date_str] = set()
                    daily_tx_count[date_str] = 0
                    
                daily_addresses[date_str].add(tx.get("from", "").lower())
                daily_addresses[date_str].add(tx.get("to", "").lower())
                daily_tx_count[date_str] += 1
                
            # Insert snapshots for each day with data
            for date_str, addresses in daily_addresses.items():
                addresses.discard("")  # Remove empty
                
                dau_data = {
                    "coin_id": coin_id,
                    "chain_slug": chain_slug,
                    "date": datetime.fromisoformat(date_str).date(),
                    "active_addresses": len(addresses),
                    "tx_count": daily_tx_count[date_str],
                }
                
                await self._save_dau_snapshot(dau_data)
                seeded["dau_snapshots"].append({
                    "date": date_str,
                    "dau": len(addresses),
                    "tx_count": daily_tx_count[date_str],
                })
                seeded["days_seeded"] += 1
                
            logger.info(f"Seeded {seeded['days_seeded']} days of data for {coin_id}")
            
        except Exception as e:
            logger.error(f"Failed to seed historical data for {coin_id}: {e}")
            
        return seeded
        
    async def collect_and_analyze(
        self,
        coin_id: str,
        chain_slug: str = "ethereum",
        chain_id: int = 1,
        contract_address: str = None,
        token_price_usd: float = 0,
        token_decimals: int = 18,
    ) -> Dict[str, Any]:
        """
        Main entry point: Collect all on-chain data and calculate signals
        
        Args:
            coin_id: Coin identifier
            chain_slug: Chain slug (default ethereum)
            chain_id: Chain ID (default 1)
            contract_address: Token contract (None for native tokens)
            token_price_usd: Current token price
            token_decimals: Token decimals
            
        Returns:
            Complete on-chain signals dict
        """
        logger.info(f"Collecting on-chain data for {coin_id}")
        
        result = {
            "coin_id": coin_id,
            "whale_signals": {},
            "dau_signals": {},
            "holder_signals": {},
            "overall": {},
        }
        
        try:
            # Load exchange addresses if not loaded
            if not EXCHANGE_ADDRESSES:
                await self.load_exchange_addresses()
                
            # Collect whale transactions
            if contract_address and token_price_usd > 0:
                whale_txs = await self.collect_whale_transactions(
                    coin_id, chain_slug, chain_id, contract_address,
                    token_price_usd, token_decimals
                )
                await self.save_whale_transactions(whale_txs)
            elif token_price_usd > 0:
                whale_txs = await self.collect_native_whale_transactions(
                    coin_id, chain_slug, chain_id, token_price_usd
                )
                await self.save_whale_transactions(whale_txs)
                
            # Calculate signals from stored data
            whale_signals = await self.calculate_whale_signals(coin_id)
            dau_signals = await self.calculate_dau_signals(coin_id)
            holder_signals = await self.calculate_holder_signals(coin_id)
            
            # Calculate overall
            overall = await self.calculate_overall_signal(
                whale_signals, dau_signals, holder_signals
            )
            
            result["whale_signals"] = whale_signals
            result["dau_signals"] = dau_signals
            result["holder_signals"] = holder_signals
            result["overall"] = overall
            
            logger.info(f"On-chain analysis complete for {coin_id}: {overall}")
            
        except Exception as e:
            logger.error(f"Failed to collect/analyze {coin_id}: {e}")
            
        return result
    
    # =========================================================================
    # WHALE BEHAVIORAL PROFILING (Intent Divergence Engine)
    # =========================================================================
    
    async def get_whale_historical_behavior(
        self,
        address: str,
        chain_id: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Analyze last N transactions to assign behavior_label.
        
        Behavior Labels:
        - value_hunter: Buys when RSI < 30 (oversold conditions)
        - news_front_runner: Moves 1-2h before major news/sentiment spikes
        - panic_seller: Sells during 5%+ price drops
        - accumulator: Steady buying pattern regardless of conditions
        - mixed: No clear pattern
        
        Args:
            address: Whale wallet address
            chain_id: Chain ID
            limit: Number of transactions to analyze
            
        Returns:
            Behavioral profile dict
        """
        from sqlalchemy import text
        
        # Fetch transaction history with market context
        query = text("""
            SELECT 
                tx_type,
                amount_usd,
                rsi_at_tx,
                sentiment_at_tx,
                price_change_24h_at_tx,
                is_profitable,
                profit_pct,
                tx_timestamp
            FROM whale_transaction_history
            WHERE address = :address
            ORDER BY tx_timestamp DESC
            LIMIT :limit
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {"address": address.lower(), "limit": limit})
                transactions = [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            logger.warning(f"No transaction history for {address}: {e}")
            transactions = []
        
        if len(transactions) < 5:
            return {
                "address": address,
                "behavior_label": "unknown",
                "behavior_confidence": 0,
                "total_transactions": len(transactions),
                "analysis": "Insufficient transaction history",
            }
        
        # Analyze patterns
        return self._classify_whale_behavior(address, transactions)
    
    def _classify_whale_behavior(
        self,
        address: str,
        transactions: List[Dict],
    ) -> Dict[str, Any]:
        """Classify whale behavior based on transaction patterns"""
        
        total = len(transactions)
        buys = [t for t in transactions if t.get("tx_type") == "buy"]
        sells = [t for t in transactions if t.get("tx_type") == "sell"]
        
        # Count pattern indicators
        buys_at_oversold = sum(1 for t in buys if (t.get("rsi_at_tx") or 50) < 30)
        buys_at_fear = sum(1 for t in buys if (t.get("sentiment_at_tx") or 50) < 30)
        sells_during_drops = sum(1 for t in sells if (t.get("price_change_24h_at_tx") or 0) < -5)
        sells_at_greed = sum(1 for t in sells if (t.get("sentiment_at_tx") or 50) > 70)
        
        profitable = sum(1 for t in transactions if t.get("is_profitable"))
        avg_profit = sum(t.get("profit_pct") or 0 for t in transactions) / max(total, 1)
        
        # Determine dominant behavior
        scores = {
            "value_hunter": (buys_at_oversold + buys_at_fear) / max(len(buys), 1) if buys else 0,
            "panic_seller": sells_during_drops / max(len(sells), 1) if sells else 0,
            "accumulator": len(buys) / max(total, 1),
            "distributor": len(sells) / max(total, 1),
        }
        
        # Check for news front-runner (would need news correlation - simplified here)
        # This would ideally check if trades happened 1-2h before sentiment spikes
        
        # Get dominant behavior
        best_label = max(scores, key=scores.get)
        best_score = scores[best_label]
        
        # If no strong pattern, mark as mixed
        if best_score < 0.4:
            best_label = "mixed"
            best_score = 0.3
        
        return {
            "address": address,
            "behavior_label": best_label,
            "behavior_confidence": round(best_score, 2),
            "total_transactions": total,
            "profitable_trades": profitable,
            "success_rate": round(profitable / max(total, 1), 2),
            "avg_profit_pct": round(avg_profit, 2),
            "pattern_scores": scores,
            "buys_at_oversold": buys_at_oversold,
            "sells_during_drops": sells_during_drops,
        }
    
    async def calculate_reaction_latency(
        self,
        address: str,
        coin_id: str,
    ) -> int:
        """
        Calculate average minutes between sentiment spike and whale transaction.
        
        Returns:
            Average reaction latency in minutes (0 if no data)
        """
        from sqlalchemy import text
        
        # Find transactions close to sentiment spikes
        query = text("""
            WITH sentiment_spikes AS (
                SELECT analyzed_at, sentiment_score
                FROM behavioral_sentiment
                WHERE coin_id = :coin_id
                AND (sentiment_score < 25 OR sentiment_score > 75)
                ORDER BY analyzed_at DESC
                LIMIT 20
            )
            SELECT 
                wth.tx_timestamp,
                ss.analyzed_at as spike_time,
                EXTRACT(EPOCH FROM (wth.tx_timestamp - ss.analyzed_at)) / 60 as latency_minutes
            FROM whale_transaction_history wth
            CROSS JOIN sentiment_spikes ss
            WHERE wth.address = :address
            AND wth.coin_id = :coin_id
            AND ABS(EXTRACT(EPOCH FROM (wth.tx_timestamp - ss.analyzed_at))) < 7200  -- Within 2 hours
            ORDER BY ABS(EXTRACT(EPOCH FROM (wth.tx_timestamp - ss.analyzed_at)))
            LIMIT 20
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {
                    "address": address.lower(),
                    "coin_id": coin_id,
                })
                rows = result.fetchall()
                
                if not rows:
                    return 0
                
                latencies = [abs(row[2]) for row in rows if row[2] is not None]
                return int(sum(latencies) / len(latencies)) if latencies else 0
                
        except Exception as e:
            logger.warning(f"Failed to calculate reaction latency: {e}")
            return 0
    
    async def update_whale_profile(
        self,
        address: str,
        behavior_data: Dict[str, Any],
        chain_id: int = 1,
    ) -> bool:
        """
        Save or update whale behavioral profile.
        
        Args:
            address: Whale address
            behavior_data: Output from get_whale_historical_behavior()
            chain_id: Chain ID
            
        Returns:
            True on success
        """
        from sqlalchemy import text
        from datetime import datetime
        
        query = text("""
            INSERT INTO whale_behavioral_profiles (
                address, chain_id, behavior_label, behavior_confidence,
                success_rate, total_transactions, profitable_trades,
                last_active, updated_at
            ) VALUES (
                :address, :chain_id, :behavior_label, :behavior_confidence,
                :success_rate, :total_transactions, :profitable_trades,
                NOW(), NOW()
            )
            ON CONFLICT (address) DO UPDATE SET
                behavior_label = EXCLUDED.behavior_label,
                behavior_confidence = EXCLUDED.behavior_confidence,
                success_rate = EXCLUDED.success_rate,
                total_transactions = EXCLUDED.total_transactions,
                profitable_trades = EXCLUDED.profitable_trades,
                last_active = NOW(),
                updated_at = NOW()
        """)
        
        try:
            with self.db.engine.begin() as conn:
                conn.execute(query, {
                    "address": address.lower(),
                    "chain_id": chain_id,
                    "behavior_label": behavior_data.get("behavior_label", "unknown"),
                    "behavior_confidence": behavior_data.get("behavior_confidence", 0),
                    "success_rate": behavior_data.get("success_rate", 0),
                    "total_transactions": behavior_data.get("total_transactions", 0),
                    "profitable_trades": behavior_data.get("profitable_trades", 0),
                })
            
            logger.info(f"Updated whale profile: {address[:10]}... -> {behavior_data.get('behavior_label')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update whale profile: {e}")
            return False
    
    async def save_transaction_with_context(
        self,
        address: str,
        coin_id: str,
        tx_hash: str,
        tx_type: str,
        amount_usd: float,
        market_context: Dict[str, Any],
        chain_id: int = 1,
    ) -> bool:
        """
        Save whale transaction with market context for behavior analysis.
        
        Args:
            address: Whale address
            coin_id: Coin ID
            tx_hash: Transaction hash
            tx_type: buy/sell/transfer
            amount_usd: Transaction value in USD
            market_context: Dict with price, rsi, sentiment at transaction time
            chain_id: Chain ID
            
        Returns:
            True on success
        """
        from sqlalchemy import text
        from datetime import datetime
        
        query = text("""
            INSERT INTO whale_transaction_history (
                address, coin_id, chain_id, tx_hash, tx_type, amount_usd,
                price_at_tx, price_change_24h_at_tx, rsi_at_tx, sentiment_at_tx,
                tx_timestamp
            ) VALUES (
                :address, :coin_id, :chain_id, :tx_hash, :tx_type, :amount_usd,
                :price_at_tx, :price_change_24h_at_tx, :rsi_at_tx, :sentiment_at_tx,
                NOW()
            )
            ON CONFLICT DO NOTHING
        """)
        
        try:
            with self.db.engine.begin() as conn:
                conn.execute(query, {
                    "address": address.lower(),
                    "coin_id": coin_id,
                    "chain_id": chain_id,
                    "tx_hash": tx_hash,
                    "tx_type": tx_type,
                    "amount_usd": amount_usd,
                    "price_at_tx": market_context.get("price", 0),
                    "price_change_24h_at_tx": market_context.get("price_change_24h", 0),
                    "rsi_at_tx": market_context.get("rsi", 50),
                    "sentiment_at_tx": market_context.get("sentiment_score", 50),
                })
            return True
            
        except Exception as e:
            logger.error(f"Failed to save transaction context: {e}")
            return False
    
    async def get_active_whale_profiles(
        self,
        coin_id: str = None,
        hours_back: int = 24,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get profiles of whales active in the last N hours.
        
        Args:
            coin_id: Optional coin filter
            hours_back: Hours to look back
            limit: Max profiles to return
            
        Returns:
            List of whale profile dicts
        """
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                wp.address,
                wp.behavior_label,
                wp.behavior_confidence,
                wp.success_rate,
                wp.total_transactions,
                wp.last_active
            FROM whale_behavioral_profiles wp
            WHERE wp.last_active > NOW() - INTERVAL ':hours hours'
            ORDER BY wp.success_rate DESC, wp.total_transactions DESC
            LIMIT :limit
        """.replace(":hours", str(hours_back)))
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get active whale profiles: {e}")
            return []
        
    async def update_onchain_signals(
        self,
        coin_id: str,
        whale_txs: List[Dict] = None,
    ) -> bool:
        """
        Calculate and upsert on-chain signals for a coin.
        This is the main method called by scheduler after collecting whale transactions.
        
        Args:
            coin_id: Coin identifier
            whale_txs: Optional list of whale transactions (for reference)
            
        Returns:
            True on success
        """
        from sqlalchemy import text
        from datetime import datetime
        
        try:
            # Calculate all signals from stored data
            whale_signals = await self.calculate_whale_signals(coin_id)
            dau_signals = await self.calculate_dau_signals(coin_id)
            holder_signals = await self.calculate_holder_signals(coin_id)
            overall = await self.calculate_overall_signal(
                whale_signals, dau_signals, holder_signals
            )
            
            # Upsert to onchain_signals table
            query = text("""
                INSERT INTO onchain_signals (
                    coin_id, overall_signal, bullish_probability, confidence_score,
                    whale_signal, whale_tx_count_24h, whale_tx_change_pct, 
                    whale_net_flow_usd, whale_inflow_usd, whale_outflow_usd,
                    network_signal, dau_current, dau_prev_day, dau_change_1d_pct, dau_trend,
                    holder_signal, top10_change_pct, accumulation_score,
                    last_whale_update, last_dau_update, updated_at
                ) VALUES (
                    :coin_id, :overall_signal, :bullish_probability, :confidence_score,
                    :whale_signal, :whale_tx_count_24h, :whale_tx_change_pct,
                    :whale_net_flow_usd, :whale_inflow_usd, :whale_outflow_usd,
                    :network_signal, :dau_current, :dau_prev_day, :dau_change_1d_pct, :dau_trend,
                    :holder_signal, :top10_change_pct, :accumulation_score,
                    :last_whale_update, :last_dau_update, :updated_at
                )
                ON CONFLICT (coin_id) DO UPDATE SET
                    overall_signal = EXCLUDED.overall_signal,
                    bullish_probability = EXCLUDED.bullish_probability,
                    confidence_score = EXCLUDED.confidence_score,
                    whale_signal = EXCLUDED.whale_signal,
                    whale_tx_count_24h = EXCLUDED.whale_tx_count_24h,
                    whale_tx_change_pct = EXCLUDED.whale_tx_change_pct,
                    whale_net_flow_usd = EXCLUDED.whale_net_flow_usd,
                    whale_inflow_usd = EXCLUDED.whale_inflow_usd,
                    whale_outflow_usd = EXCLUDED.whale_outflow_usd,
                    network_signal = EXCLUDED.network_signal,
                    dau_current = EXCLUDED.dau_current,
                    dau_prev_day = EXCLUDED.dau_prev_day,
                    dau_change_1d_pct = EXCLUDED.dau_change_1d_pct,
                    dau_trend = EXCLUDED.dau_trend,
                    holder_signal = EXCLUDED.holder_signal,
                    top10_change_pct = EXCLUDED.top10_change_pct,
                    accumulation_score = EXCLUDED.accumulation_score,
                    last_whale_update = EXCLUDED.last_whale_update,
                    last_dau_update = EXCLUDED.last_dau_update,
                    updated_at = EXCLUDED.updated_at
            """)
            
            now = datetime.now()
            
            with self.db.engine.begin() as conn:
                conn.execute(query, {
                    "coin_id": coin_id,
                    "overall_signal": overall.get("overall_signal", "NEUTRAL"),
                    "bullish_probability": overall.get("bullish_probability", 50),
                    "confidence_score": overall.get("confidence_score", 0),
                    # Whale signals
                    "whale_signal": whale_signals.get("whale_signal", "NEUTRAL"),
                    "whale_tx_count_24h": whale_signals.get("whale_tx_count_24h", 0),
                    "whale_tx_change_pct": whale_signals.get("whale_tx_change_pct", 0),
                    "whale_net_flow_usd": whale_signals.get("whale_net_flow_usd", 0),
                    "whale_inflow_usd": whale_signals.get("whale_inflow_usd", 0),
                    "whale_outflow_usd": whale_signals.get("whale_outflow_usd", 0),
                    # DAU/Network signals
                    "network_signal": dau_signals.get("network_signal", "NEUTRAL"),
                    "dau_current": dau_signals.get("dau_current", 0),
                    "dau_prev_day": dau_signals.get("dau_prev_day", 0),
                    "dau_change_1d_pct": dau_signals.get("dau_change_1d_pct", 0),
                    "dau_trend": dau_signals.get("dau_trend", "STABLE"),
                    # Holder signals
                    "holder_signal": holder_signals.get("holder_signal", "NEUTRAL"),
                    "top10_change_pct": holder_signals.get("top10_change_pct", 0),
                    "accumulation_score": holder_signals.get("accumulation_score", 50),
                    # Timestamps
                    "last_whale_update": now if whale_txs else None,
                    "last_dau_update": now,
                    "updated_at": now,
                })
            
            logger.info(f"Updated onchain signals for {coin_id}: {overall.get('overall_signal')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update onchain signals for {coin_id}: {e}")
            return False
        
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

