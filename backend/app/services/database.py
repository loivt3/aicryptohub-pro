"""
AI Crypto Hub Pro - Database Service
SQLAlchemy connection and operations for PostgreSQL
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config import get_settings

logger = logging.getLogger(__name__)


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
            timeframe: Candle timeframe (not used - single timeframe table)
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV dictionaries
        """
        # Get symbol from coins table dynamically
        symbol = self._get_symbol_for_coin(coin_id)
        
        if not symbol:
            logger.warning(f"No symbol found for coin_id: {coin_id}")
            return []
        
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
            WHERE symbol = :symbol
            ORDER BY open_time DESC
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "symbol": symbol,
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


# Dependency injection
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get database service instance (FastAPI dependency)"""
    global _db_service
    if _db_service is None:
        settings = get_settings()
        _db_service = DatabaseService(settings.database_url)
    return _db_service
