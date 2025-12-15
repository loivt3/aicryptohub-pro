"""
On-Chain Data Collector Service for AI Hub
Collects whale transactions, DAU, and top holder data from Etherscan V2 API
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import httpx

logger = logging.getLogger(__name__)

# Etherscan V2 unified endpoint
ETHERSCAN_V2_BASE = "https://api.etherscan.io/v2/api"

# Whale threshold in USD
WHALE_THRESHOLD_USD = 100_000

# Known exchange addresses (loaded from DB at runtime)
EXCHANGE_ADDRESSES: Dict[str, Dict] = {}


class OnChainCollector:
    """
    Collector service for on-chain data:
    - Whale transactions (>$100K)
    - Daily Active Addresses (DAU)
    - Top holder tracking
    """
    
    REQUEST_DELAY = 0.25  # 4 requests/sec for Etherscan free tier
    
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
    ) -> Optional[Dict]:
        """
        Make request to Etherscan V2 unified API
        
        Args:
            chain_id: Chain ID (1 for ETH, 56 for BSC, etc.)
            params: API parameters
            
        Returns:
            API response or None on error
        """
        await self._rate_limit()
        
        try:
            client = await self._get_client()
            
            # Build params with chainid and apikey
            # Etherscan V2 requires chainid as a parameter
            params["chainid"] = chain_id
            params["apikey"] = self.api_key
            
            # Use base URL without query string
            url = ETHERSCAN_V2_BASE
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for success - Etherscan V2 uses different response format
            if data.get("status") == "1":
                return data
            elif data.get("result") and isinstance(data.get("result"), list):
                # Some endpoints return result directly without status
                return data
            else:
                error_msg = data.get("message") or data.get("result") or "Unknown error"
                logger.warning(f"Etherscan error for chain {chain_id}: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Etherscan request failed: {e}")
            return None
            
    async def load_exchange_addresses(self):
        """Load known exchange addresses from database"""
        global EXCHANGE_ADDRESSES
        
        try:
            query = """
                SELECT address, chain_slug, label, exchange_name, is_deposit
                FROM known_addresses
                WHERE address_type = 'exchange'
            """
            rows = await self.db.fetch_all(query)
            
            for row in rows:
                addr = row['address'].lower()
                EXCHANGE_ADDRESSES[addr] = {
                    'label': row['label'],
                    'exchange': row['exchange_name'],
                    'is_deposit': row['is_deposit'],
                }
                
            logger.info(f"Loaded {len(EXCHANGE_ADDRESSES)} known exchange addresses")
            
        except Exception as e:
            logger.error(f"Failed to load exchange addresses: {e}")
            
    def _is_exchange_address(self, address: str) -> Optional[Dict]:
        """Check if address is a known exchange wallet"""
        return EXCHANGE_ADDRESSES.get(address.lower())
        
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
        Collect whale transactions (>$100K) for a token
        
        Uses Etherscan tokentx API to get ERC20 transfers
        Filters by USD value threshold
        
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
        
        try:
            # Calculate block range (approximate)
            # ETH: ~12 sec/block, BSC: ~3 sec/block
            blocks_per_hour = 300 if chain_id == 1 else 1200
            start_block = 'latest'  # Will paginate backwards
            
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
                
                # Filter by whale threshold
                if usd_value >= WHALE_THRESHOLD_USD:
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
                    
            logger.info(f"Found {len(whale_txs)} whale transactions for {coin_id}")
            
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
        
        if not self.api_key or native_price_usd <= 0:
            logger.warning(f"Cannot collect native whale txs: missing API key or price")
            return whale_txs
            
        try:
            # For native tokens, we look at large transfers to/from known exchange addresses
            # We'll query multiple exchange addresses
            exchange_addrs = list(EXCHANGE_ADDRESSES.keys())[:10]  # Top 10 exchanges
            
            cutoff_timestamp = datetime.utcnow() - timedelta(hours=hours_back)
            
            for exchange_addr in exchange_addrs:
                if not exchange_addr:
                    continue
                    
                # Get transactions for this exchange address
                params = {
                    "module": "account",
                    "action": "txlist",
                    "address": exchange_addr,
                    "page": 1,
                    "offset": 50,  # Limit per exchange
                    "sort": "desc",
                }
                
                response = await self._etherscan_request(chain_id, params)
                
                if not response or not response.get("result"):
                    continue
                    
                for tx in response.get("result", []):
                    # Skip failed transactions
                    if tx.get("isError") == "1":
                        continue
                        
                    # Parse timestamp
                    tx_time = datetime.fromtimestamp(int(tx.get("timeStamp", 0)))
                    
                    if tx_time < cutoff_timestamp:
                        break  # Stop if older than cutoff
                        
                    # Calculate value in USD (native token value is in wei)
                    raw_value = int(tx.get("value", 0))
                    native_value = raw_value / (10 ** 18)  # Native tokens use 18 decimals
                    usd_value = native_value * native_price_usd
                    
                    # Filter by whale threshold
                    if usd_value >= WHALE_THRESHOLD_USD:
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
                            "value_native": native_value,
                            "tx_type": tx_type,
                            "is_exchange_related": True,  # Always true for exchange-focused queries
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
            # Get whale tx count for current period
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
            
            # Get previous period for comparison
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
            net_flow = inflow - outflow  # Positive = bearish (more going to exchanges)
            
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
            today_start = datetime.combine(today, datetime.min.time())
            
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
            
            # Save to database
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
            # Get last 7 days of DAU data
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
            
            # Calculate changes
            def calc_change(current, prev):
                if prev > 0:
                    return ((current - prev) / prev) * 100
                return 0
                
            change_1d = calc_change(dau_current, dau_prev_day)
            change_3d = calc_change(dau_current, dau_3d_ago)
            change_7d = calc_change(dau_current, dau_7d_ago)
            
            # Calculate 7-day average
            dau_avg_7d = sum(r['active_addresses'] for r in rows) / len(rows)
            
            # Determine trend
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
        
        Note: This API may require paid tier for some chains
        
        Args:
            coin_id: Coin identifier
            chain_slug: Chain slug
            chain_id: Chain ID
            contract_address: Token contract
            limit: Number of holders to fetch
            
        Returns:
            List of top holders
        """
        try:
            # Etherscan doesn't have direct top holders API for all tokens
            # We'll use TokenHolderList for verified tokens
            params = {
                "module": "token",
                "action": "tokenholderlist",
                "contractaddress": contract_address,
                "page": 1,
                "offset": min(limit, 100),
            }
            
            response = await self._etherscan_request(chain_id, params)
            
            if not response or not response.get("result"):
                logger.warning(f"No holder data for {coin_id}")
                return []
                
            holders = []
            for idx, holder in enumerate(response.get("result", []), 1):
                holders.append({
                    "rank": idx,
                    "address": holder.get("TokenHolderAddress", ""),
                    "balance": holder.get("TokenHolderQuantity", "0"),
                    "pct": 0,  # Would need total supply calculation
                })
                
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
            # Get latest and 7-day-ago snapshots
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
                    "accumulation_score": 50,  # Neutral
                    "holder_signal": "NEUTRAL",
                }
                
            current = float(rows[0]['top10_total_balance'] or 0)
            prev_7d = float(rows[-1]['top10_total_balance'] or 0)
            
            if prev_7d > 0:
                change_pct = ((current - prev_7d) / prev_7d) * 100
            else:
                change_pct = 0
                
            # Calculate accumulation score (0-100)
            # >5% accumulation = 80+
            # Distribution = <20
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
        bullish_prob = (score + 1) * 50  # Maps -1..1 to 0..100
        
        # Determine overall signal
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
        
        # Initialize with defaults
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
                # ERC20 token - use tokentx API
                whale_txs = await self.collect_whale_transactions(
                    coin_id, chain_slug, chain_id, contract_address,
                    token_price_usd, token_decimals
                )
                await self.save_whale_transactions(whale_txs)
            elif token_price_usd > 0:
                # Native token (ETH, BNB) - use txlist API
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
        
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
