"""
AI Crypto Hub Pro - Database Service
SQLAlchemy connection and operations for PostgreSQL
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# Columns that should remain as strings (not converted to float)
STRING_COLUMNS = {'coin_id', 'symbol', 'name', 'image', 'last_updated', 'provider', 'reason', 'signal', 'analyzed_at'}


def convert_db_value(col: str, val: Any) -> Any:
    """Convert database values to JSON-serializable types"""
    if val is None:
        return None
    if col in STRING_COLUMNS:
        return str(val) if val else val
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (int, float)):
        return float(val)
    # Try to convert string numbers
    if isinstance(val, str):
        try:
            return float(val)
        except (ValueError, TypeError):
            return val
    return val


class DatabaseService:
    """Database service for PostgreSQL operations"""
    
    def __init__(self, database_url: str):
        """Initialize database connection"""
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        
    @property
    def engine(self):
        """Lazy-load database engine"""
        if self._engine is None:
            settings = get_settings()
            
            # Fix for Supabase pooler SASL authentication issue
            connect_args = {
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
            
            # Add SSL for Supabase
            if "supabase" in self.database_url:
                connect_args["sslmode"] = "require"
            
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_pre_ping=True,
                pool_recycle=300,  # Recycle connections every 5 min
                connect_args=connect_args,
            )
        return self._engine
    
    @property
    def session_factory(self):
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_market_data(self, limit: int = 100, orderby: str = "market_cap") -> List[Dict[str, Any]]:
        """
        Get market data for all coins
        
        Args:
            limit: Max number of coins to return
            orderby: Column to order by
            
        Returns:
            List of coin data dicts
        """
        order_column = "market_cap" if orderby == "market_cap" else orderby
        
        query = text(f"""
            SELECT 
                coin_id,
                symbol,
                name,
                image_url as image,
                price,
                price_change_1h as change_1h,
                change_24h,
                price_change_7d as change_7d,
                market_cap,
                rank as market_cap_rank,
                volume_24h,
                high_24h,
                low_24h,
                last_updated
            FROM aihub_coins
            WHERE price > 0
            ORDER BY {order_column} DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                rows = result.fetchall()
                columns = result.keys()
                
                return [
                    {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return []
    
    def get_coin_by_id(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get single coin data by coin_id"""
        query = text("""
            SELECT 
                coin_id,
                symbol,
                name,
                image_url as image,
                price,
                price_change_1h as change_1h,
                change_24h,
                price_change_7d as change_7d,
                price_change_30d as change_30d,
                market_cap,
                rank as market_cap_rank,
                volume_24h,
                high_24h,
                low_24h,
                last_updated
            FROM aihub_coins
            WHERE coin_id = :coin_id
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                return None
        except Exception as e:
            logger.error(f"Failed to fetch coin {coin_id}: {e}")
            return None
    
    def get_sentiment_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sentiment data for all coins"""
        query = text("""
            SELECT 
                c.coin_id,
                c.symbol,
                c.name,
                COALESCE(s.sentiment_score * 100, 50) as asi_score,
                COALESCE(s.ai_signal, 'HOLD') as signal,
                s.sentiment_reason as reason,
                s.provider,
                s.analyzed_at
            FROM aihub_coins c
            LEFT JOIN aihub_sentiment s ON UPPER(c.symbol) = UPPER(s.symbol)
            WHERE c.price > 0
            ORDER BY c.market_cap DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                rows = result.fetchall()
                columns = result.keys()
                
                return [
                    {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to fetch sentiment data: {e}")
            return []
    
    def get_coin_sentiment(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get sentiment data for a specific coin (by coin_id or symbol)"""
        query = text("""
            SELECT 
                c.coin_id,
                c.symbol,
                c.name,
                COALESCE(s.sentiment_score * 100, 50) as asi_score,
                COALESCE(s.ai_signal, 'HOLD') as signal,
                s.sentiment_reason as reason,
                s.provider,
                s.analyzed_at
            FROM aihub_coins c
            LEFT JOIN aihub_sentiment s ON UPPER(c.symbol) = UPPER(s.symbol)
            WHERE c.coin_id = :coin_id 
               OR UPPER(c.symbol) = UPPER(:coin_id)
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    data = {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    # Ensure asi_score is an integer
                    data['asi_score'] = int(data.get('asi_score') or 50)
                    return data
                return None
        except Exception as e:
            logger.error(f"Failed to fetch sentiment for {coin_id}: {e}")
            return None

    def get_onchain_signals(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get on-chain signals for a specific coin from onchain_signals table"""
        query = text("""
            SELECT 
                coin_id,
                -- Whale Activity
                whale_tx_count_24h,
                whale_tx_change_pct,
                whale_inflow_usd,
                whale_outflow_usd,
                whale_net_flow_usd,
                whale_signal,
                -- Network Health / DAU
                dau_current,
                dau_prev_day,
                dau_change_1d_pct,
                dau_trend,
                network_signal,
                -- Top Holders
                top10_change_pct,
                accumulation_score,
                holder_signal,
                -- Overall
                overall_signal,
                bullish_probability,
                confidence_score,
                ai_prediction,
                ai_summary,
                -- Metadata
                last_whale_update,
                last_dau_update,
                updated_at
            FROM onchain_signals
            WHERE coin_id = :coin_id
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                return None
        except Exception as e:
            logger.error(f"Failed to fetch onchain signals for {coin_id}: {e}")
            return None

    def get_onchain_summary(self) -> Dict[str, Any]:
        """Get on-chain summary for top coins"""
        query = text("""
            SELECT 
                coin_id,
                overall_signal,
                bullish_probability,
                whale_net_flow_usd,
                whale_signal,
                dau_current,
                dau_change_1d_pct,
                network_signal,
                updated_at
            FROM onchain_signals
            ORDER BY updated_at DESC NULLS LAST
            LIMIT 20
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                columns = result.keys()
                
                return [
                    {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to fetch onchain summary: {e}")
            return []
    
    def get_coins_with_contracts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get coins with contract addresses for on-chain tracking.
        Uses coin_contracts table or fallback to known mappings.
        
        Args:
            limit: Max number of coins to return
            
        Returns:
            List of coins with contract_address, chain_id, price
        """
        # Try to get from coin_contracts table first
        query = text("""
            SELECT 
                c.coin_id,
                c.symbol,
                c.price,
                c.market_cap,
                cc.contract_address,
                cc.chain_id,
                cc.chain_slug,
                cc.decimals
            FROM aihub_coins c
            INNER JOIN coin_contracts cc ON c.coin_id = cc.coin_id
            WHERE c.price > 0 
              AND cc.contract_address IS NOT NULL
              AND cc.chain_id IN (1, 56, 137, 42161, 10)  -- ETH, BSC, Polygon, Arbitrum, Optimism
            ORDER BY c.market_cap DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                rows = result.fetchall()
                
                if rows:
                    columns = result.keys()
                    return [
                        {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                        for row in rows
                    ]
        except Exception as e:
            logger.warning(f"coin_contracts table not available: {e}")
        
        # Fallback: Return top coins with hardcoded ETH contracts for major tokens
        # These are verified ERC-20 contract addresses
        KNOWN_CONTRACTS = {
            "ethereum": {"contract": None, "chain_id": 1, "decimals": 18},  # Native ETH
            "tether": {"contract": "0xdac17f958d2ee523a2206206994597c13d831ec7", "chain_id": 1, "decimals": 6},
            "usd-coin": {"contract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "chain_id": 1, "decimals": 6},
            "binancecoin": {"contract": None, "chain_id": 56, "decimals": 18},  # Native BNB
            "staked-ether": {"contract": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84", "chain_id": 1, "decimals": 18},
            "wrapped-bitcoin": {"contract": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "chain_id": 1, "decimals": 8},
            "chainlink": {"contract": "0x514910771af9ca656af840dff83e8264ecf986ca", "chain_id": 1, "decimals": 18},
            "uniswap": {"contract": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984", "chain_id": 1, "decimals": 18},
            "matic-network": {"contract": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", "chain_id": 1, "decimals": 18},
            "dai": {"contract": "0x6b175474e89094c44da98b954eedeac495271d0f", "chain_id": 1, "decimals": 18},
            "shiba-inu": {"contract": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce", "chain_id": 1, "decimals": 18},
            "pepe": {"contract": "0x6982508145454ce325ddbe47a25d4ec3d2311933", "chain_id": 1, "decimals": 18},
        }
        
        fallback_query = text("""
            SELECT coin_id, symbol, price, market_cap
            FROM aihub_coins
            WHERE price > 0 AND coin_id = ANY(:coin_ids)
            ORDER BY market_cap DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(fallback_query, {
                    "coin_ids": list(KNOWN_CONTRACTS.keys()),
                    "limit": limit,
                })
                rows = result.fetchall()
                
                coins = []
                for row in rows:
                    coin_id = row[0]
                    contract_info = KNOWN_CONTRACTS.get(coin_id, {})
                    
                    if contract_info.get("contract"):  # Skip native tokens
                        coins.append({
                            "coin_id": coin_id,
                            "symbol": row[1],
                            "price": float(row[2]) if row[2] else 0,
                            "market_cap": float(row[3]) if row[3] else 0,
                            "contract_address": contract_info["contract"],
                            "chain_id": contract_info["chain_id"],
                            "chain_slug": "ethereum",
                            "decimals": contract_info["decimals"],
                        })
                
                logger.info(f"Returning {len(coins)} coins with known contracts for on-chain tracking")
                return coins
                
        except Exception as e:
            logger.error(f"Failed to get coins with contracts: {e}")
            return []
    
    def _get_symbol_for_coin(self, coin_id: str) -> Optional[str]:
        """
        Get trading symbol for a coin_id dynamically from coins table
        
        Args:
            coin_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Symbol in uppercase (e.g., 'BTC', 'ETH') or None if not found
        """
        # First try to get from aihub_coins table
        query = text("""
            SELECT UPPER(symbol) as symbol
            FROM aihub_coins 
            WHERE coin_id = :coin_id
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row and row[0]:
                    return row[0]
                
                # Fallback: try uppercase of coin_id
                # For coins like 'BTC' sent directly
                return coin_id.upper()
                
        except Exception as e:
            logger.warning(f"Error fetching symbol for {coin_id}: {e}")
            # Fallback to uppercase
            return coin_id.upper()
    
    def get_ohlcv_data(
        self,
        coin_id: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data for a coin from aihub_ohlcv table
        
        Args:
            coin_id: Coin identifier (e.g., 'bitcoin' -> 'BTC', 'ethereum' -> 'ETH')
            timeframe: Candle timeframe - '1m', '1h', '4h', '1d', '1w'
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV dictionaries
        """
        # Timeframe to DB code mapping
        TIMEFRAME_TO_DB_CODE = {
            "1h": 1,
            "4h": 4,
            "1d": 24,
            "1w": 168,
            "1M": 720,  # 1 month
        }
        
        # Get symbol from coins table dynamically
        symbol = self._get_symbol_for_coin(coin_id)
        
        if not symbol:
            logger.warning(f"No symbol found for coin_id: {coin_id}")
            return []
        
        # Get DB code for timeframe (default to 1h)
        tf_code = TIMEFRAME_TO_DB_CODE.get(timeframe, 1)
        
        query = text("""
            SELECT 
                symbol,
                open,
                high,
                low,
                close,
                volume,
                open_time
            FROM aihub_ohlcv
            WHERE symbol = :symbol AND timeframe = :timeframe
            ORDER BY open_time DESC
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "symbol": symbol,
                    "timeframe": tf_code,
                    "limit": limit
                })
                rows = result.fetchall()
                
                return [
                    {
                        "coin_id": row[0],
                        "open": float(row[1]) if row[1] else 0,
                        "high": float(row[2]) if row[2] else 0,
                        "low": float(row[3]) if row[3] else 0,
                        "close": float(row[4]) if row[4] else 0,
                        "volume": float(row[5]) if row[5] else 0,
                        "timestamp": row[6].isoformat() if row[6] else None,
                    }
                    for row in reversed(rows)  # Oldest first for TA
                ]
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {coin_id} ({symbol}): {e}")
            return []
    
    def get_coin_price(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get current coin price from coins table"""
        query = text("""
            SELECT 
                coin_id,
                symbol,
                name,
                current_price,
                price_change_24h,
                price_change_percentage_24h,
                volume_24h,
                market_cap,
                last_updated
            FROM coins
            WHERE coin_id = :coin_id
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row:
                    return {
                        "coin_id": row[0],
                        "symbol": row[1],
                        "name": row[2],
                        "current_price": float(row[3]) if row[3] else 0,
                        "price_change_24h": float(row[4]) if row[4] else 0,
                        "price_change_percentage_24h": float(row[5]) if row[5] else 0,
                        "volume_24h": float(row[6]) if row[6] else 0,
                        "market_cap": float(row[7]) if row[7] else 0,
                        "last_updated": row[8].isoformat() if row[8] else None,
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to fetch price for {coin_id}: {e}")
            return None
    
    def save_ai_sentiment(
        self,
        coin_id: str,
        asi_score: int,
        signal: str,
        reasoning: str,
        indicators: Dict[str, Any],
        provider: str = "python_ta"
    ) -> bool:
        """
        Save AI sentiment to aihub_sentiment table (used by PHP frontend)
        
        Args:
            coin_id: Coin identifier (e.g., 'bitcoin')
            asi_score: AI Sentiment Index (0-100)
            signal: Signal type (STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL)
            reasoning: Analysis reasoning text
            indicators: Technical indicators dict (stored as JSON)
            provider: Analysis provider name
            
        Returns:
            True if saved successfully
        """
        # Get symbol for this coin_id
        symbol = self._get_symbol_for_coin(coin_id)
        
        # Convert ASI score (0-100) to sentiment_score (0-1)
        sentiment_score = asi_score / 100.0
        
        # Write to aihub_sentiment (PHP reads from this)
        query = text("""
            INSERT INTO aihub_sentiment (symbol, ai_signal, sentiment_score, sentiment_reason, provider, analyzed_at)
            VALUES (:symbol, :signal, :sentiment_score, :reasoning, :provider, :analyzed_at)
            ON CONFLICT (symbol) DO UPDATE SET
                ai_signal = EXCLUDED.ai_signal,
                sentiment_score = EXCLUDED.sentiment_score,
                sentiment_reason = EXCLUDED.sentiment_reason,
                provider = EXCLUDED.provider,
                analyzed_at = EXCLUDED.analyzed_at
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "symbol": symbol,
                    "signal": signal,
                    "sentiment_score": sentiment_score,
                    "reasoning": reasoning,
                    "provider": provider,
                    "analyzed_at": datetime.now(),
                })
                
            logger.info(f"Saved sentiment for {coin_id} ({symbol}): {signal} ({asi_score})")
            return True
        except Exception as e:
            logger.error(f"Failed to save sentiment for {coin_id}: {e}")
            return False
    
    def get_coins_for_analysis(self, limit: int = 5000, frontend_limit: int = 100) -> List[str]:
        """
        Get list of coin IDs for analysis with TIERED PRIORITY:
        
        Priority order:
        1. ALL coins in aihub_coins (frontend) without ASI or stale ASI (>6h)
        2. ALL coins in aihub_coins with recent ASI (by market cap)
        3. By market cap
        
        Args:
            limit: Total max coins to return
            frontend_limit: Ignored (all aihub_coins are frontend)
            
        Returns:
            List of coin_ids ordered by priority
        """
        # Query: ALL coins in aihub_coins are frontend coins
        # Prioritize coins without sentiment or stale sentiment (>6h)
        query = text("""
            SELECT 
                ac.coin_id
            FROM aihub_coins ac
            INNER JOIN aihub_ohlcv ao ON UPPER(ac.symbol) = ao.symbol
            LEFT JOIN aihub_sentiment s ON UPPER(ac.symbol) = UPPER(s.symbol)
            WHERE ac.market_cap > 0
            GROUP BY ac.coin_id, ac.symbol, ac.market_cap, s.analyzed_at, s.sentiment_score
            ORDER BY 
                -- Priority 1: Coins without ASI (never analyzed)
                CASE WHEN s.analyzed_at IS NULL THEN 1
                -- Priority 2: Coins with stale ASI (>6h old)
                     WHEN s.analyzed_at < NOW() - INTERVAL '6 hours' THEN 2
                -- Priority 3: Coins with fresh ASI (by market cap)
                     ELSE 3
                END,
                ac.market_cap DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                coins = [row[0] for row in result.fetchall()]
                logger.info(f"Found {len(coins)} frontend coins for analysis (priority: no ASI > stale > fresh)")
                return coins
        except Exception as e:
            logger.error(f"Failed to get coins for analysis: {e}")
            return []

    # ===================================================
    # Generic Query Methods (for on-chain signals etc.)
    # ===================================================
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from database
        
        Args:
            query: SQL query with $1, $2 placeholders
            *args: Query parameters
            
        Returns:
            Dict with column names as keys, or None
        """
        try:
            # Convert $1, $2 style to :param style for SQLAlchemy
            sql_query = query
            params = {}
            for i, arg in enumerate(args, 1):
                sql_query = sql_query.replace(f"${i}", f":param{i}")
                params[f"param{i}"] = arg
            
            with self.get_session() as session:
                result = session.execute(text(sql_query), params)
                row = result.fetchone()
                if row:
                    # Convert Row to dict
                    return dict(row._mapping)
                return None
        except Exception as e:
            logger.error(f"fetch_one failed: {e}")
            return None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Fetch all rows from database
        
        Args:
            query: SQL query with $1, $2 placeholders
            *args: Query parameters
            
        Returns:
            List of dicts
        """
        try:
            sql_query = query
            params = {}
            for i, arg in enumerate(args, 1):
                sql_query = sql_query.replace(f"${i}", f":param{i}")
                params[f"param{i}"] = arg
            
            with self.get_session() as session:
                result = session.execute(text(sql_query), params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"fetch_all failed: {e}")
            return []
    
    async def execute(self, query: str, *args) -> bool:
        """
        Execute INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query with $1, $2 placeholders
            *args: Query parameters
            
        Returns:
            True on success
        """
        try:
            sql_query = query
            params = {}
            for i, arg in enumerate(args, 1):
                sql_query = sql_query.replace(f"${i}", f":param{i}")
                params[f"param{i}"] = arg
            
            with self.get_session() as session:
                session.execute(text(sql_query), params)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"execute failed: {e}")
            return False

    # ===================================================
    # Behavioral Sentiment Methods (AI Behavioral Alpha)
    # ===================================================
    
    def save_behavioral_sentiment(
        self,
        coin_id: str,
        symbol: str,
        sentiment_score: int,
        emotional_tone: str,
        expected_crowd_action: str,
        news_intensity: int,
        dominant_category: str,
        impact_duration: str,
        confidence_score: float = 0.5,
        reasoning: str = "",
        related_event_ids: list = None,
        whale_alignment: str = None,
        intent_divergence_score: float = None,
        raw_ai_response: str = "",
        provider: str = "gemini",
    ) -> bool:
        """
        Save behavioral sentiment analysis result.
        
        Args:
            coin_id: Coin identifier
            symbol: Coin symbol
            sentiment_score: 0-100 score
            emotional_tone: Fear/FUD/FOMO/Euphoria/Neutral
            expected_crowd_action: Sell-off/Buy-dip/Hold/etc.
            news_intensity: 1-10 intensity
            dominant_category: regulatory/technical/whale/social
            impact_duration: hours/days/weeks
            confidence_score: 0-1 confidence
            reasoning: AI reasoning text
            related_event_ids: List of news event IDs
            whale_alignment: with_crowd/against_crowd/neutral
            intent_divergence_score: -100 to +100
            raw_ai_response: Full AI response
            provider: AI provider name
            
        Returns:
            True on success
        """
        query = text("""
            INSERT INTO behavioral_sentiment (
                coin_id, symbol, sentiment_score, emotional_tone,
                expected_crowd_action, news_intensity, dominant_category,
                impact_duration, confidence_score, raw_ai_response,
                related_event_ids, whale_alignment, intent_divergence_score,
                analysis_source, analyzed_at
            ) VALUES (
                :coin_id, :symbol, :sentiment_score, :emotional_tone,
                :expected_crowd_action, :news_intensity, :dominant_category,
                :impact_duration, :confidence_score, :raw_ai_response,
                :related_event_ids, :whale_alignment, :intent_divergence_score,
                :provider, NOW()
            )
            ON CONFLICT (coin_id, analyzed_at) DO UPDATE SET
                sentiment_score = EXCLUDED.sentiment_score,
                emotional_tone = EXCLUDED.emotional_tone,
                expected_crowd_action = EXCLUDED.expected_crowd_action,
                news_intensity = EXCLUDED.news_intensity,
                dominant_category = EXCLUDED.dominant_category,
                impact_duration = EXCLUDED.impact_duration,
                confidence_score = EXCLUDED.confidence_score,
                raw_ai_response = EXCLUDED.raw_ai_response,
                related_event_ids = EXCLUDED.related_event_ids,
                whale_alignment = EXCLUDED.whale_alignment,
                intent_divergence_score = EXCLUDED.intent_divergence_score
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "coin_id": coin_id,
                    "symbol": symbol.upper(),
                    "sentiment_score": sentiment_score,
                    "emotional_tone": emotional_tone,
                    "expected_crowd_action": expected_crowd_action,
                    "news_intensity": news_intensity,
                    "dominant_category": dominant_category,
                    "impact_duration": impact_duration,
                    "confidence_score": confidence_score,
                    "raw_ai_response": raw_ai_response,
                    "related_event_ids": related_event_ids or [],
                    "whale_alignment": whale_alignment,
                    "intent_divergence_score": intent_divergence_score,
                    "provider": provider,
                })
            
            logger.info(f"Saved behavioral sentiment for {coin_id}: {emotional_tone} ({sentiment_score})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save behavioral sentiment for {coin_id}: {e}")
            return False
    
    def get_sentiment_at_time(
        self,
        coin_id: str,
        timestamp: datetime,
        window_hours: int = 2,
    ) -> Optional[Dict[str, Any]]:
        """
        Get sentiment data near a specific timestamp.
        Used for whale-sentiment correlation.
        
        Args:
            coin_id: Coin identifier
            timestamp: Target timestamp
            window_hours: Time window (±hours)
            
        Returns:
            Sentiment dict or None
        """
        from datetime import timedelta
        
        window_start = timestamp - timedelta(hours=window_hours)
        window_end = timestamp + timedelta(hours=window_hours)
        
        query = text("""
            SELECT 
                coin_id,
                sentiment_score,
                emotional_tone,
                expected_crowd_action,
                news_intensity,
                dominant_category,
                whale_alignment,
                intent_divergence_score,
                analyzed_at
            FROM behavioral_sentiment
            WHERE coin_id = :coin_id
            AND analyzed_at BETWEEN :window_start AND :window_end
            ORDER BY ABS(EXTRACT(EPOCH FROM (analyzed_at - :timestamp)))
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "coin_id": coin_id,
                    "window_start": window_start,
                    "window_end": window_end,
                    "timestamp": timestamp,
                })
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    
        except Exception as e:
            logger.error(f"Failed to get sentiment at time for {coin_id}: {e}")
        
        return None
    
    def save_news_event(
        self,
        event_id: str,
        coin_id: str,
        symbol: str,
        title: str,
        summary: str = "",
        source: str = "",
        source_url: str = "",
        category: str = "market",
        publish_time: datetime = None,
        event_time: datetime = None,
        sentiment_score: int = 50,
        emotional_tone: str = "Neutral",
        news_intensity: int = 5,
        is_front_running: bool = False,
    ) -> bool:
        """
        Save a news event for tracking.
        
        Args:
            event_id: Unique event identifier
            coin_id: Coin identifier
            symbol: Coin symbol
            title: News title
            summary: News summary
            source: News source name
            source_url: URL to news
            category: regulatory/technical/whale_movement/social_hype
            publish_time: When news was published
            event_time: When event actually happened
            sentiment_score: 0-100 score
            emotional_tone: Detected emotion
            news_intensity: 1-10 intensity
            is_front_running: Whether event happened before publish
            
        Returns:
            True on success
        """
        query = text("""
            INSERT INTO news_events (
                event_id, coin_id, symbol, title, summary, source, source_url,
                category, publish_time, event_time, sentiment_score,
                emotional_tone, news_intensity, is_front_running
            ) VALUES (
                :event_id, :coin_id, :symbol, :title, :summary, :source, :source_url,
                :category, :publish_time, :event_time, :sentiment_score,
                :emotional_tone, :news_intensity, :is_front_running
            )
            ON CONFLICT (event_id) DO UPDATE SET
                sentiment_score = EXCLUDED.sentiment_score,
                emotional_tone = EXCLUDED.emotional_tone,
                news_intensity = EXCLUDED.news_intensity,
                updated_at = NOW()
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "event_id": event_id,
                    "coin_id": coin_id,
                    "symbol": symbol.upper(),
                    "title": title,
                    "summary": summary,
                    "source": source,
                    "source_url": source_url,
                    "category": category,
                    "publish_time": publish_time or datetime.now(),
                    "event_time": event_time,
                    "sentiment_score": sentiment_score,
                    "emotional_tone": emotional_tone,
                    "news_intensity": news_intensity,
                    "is_front_running": is_front_running,
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save news event {event_id}: {e}")
            return False
    
    def get_latest_behavioral_sentiment(
        self,
        coin_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get latest behavioral sentiment for a coin"""
        query = text("""
            SELECT 
                coin_id,
                symbol,
                sentiment_score,
                emotional_tone,
                expected_crowd_action,
                news_intensity,
                dominant_category,
                impact_duration,
                whale_alignment,
                intent_divergence_score,
                confidence_score,
                analyzed_at
            FROM behavioral_sentiment
            WHERE coin_id = :coin_id
            ORDER BY analyzed_at DESC
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                
                if row:
                    columns = result.keys()
                    return {col: convert_db_value(col, val) for col, val in zip(columns, row)}
                    
        except Exception as e:
            logger.error(f"Failed to get behavioral sentiment for {coin_id}: {e}")
        
        return None


# Dependency injection
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get database service instance (FastAPI dependency)"""
    global _db_service
    if _db_service is None:
        settings = get_settings()
        _db_service = DatabaseService(settings.database_url)
    return _db_service


# Alias for compatibility
get_database_service = get_db_service


