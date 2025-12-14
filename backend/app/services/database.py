"""
Database Service - SQLAlchemy PostgreSQL Connection
Ported from python-service with improvements
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for PostgreSQL operations"""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        self.database_url = database_url or settings.DATABASE_URL
        self._engine = None
        self._session_factory = None
        
    @property
    def engine(self):
        """Lazy-load database engine"""
        if self._engine is None:
            connect_args = {
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
            
            if "supabase" in self.database_url:
                connect_args["sslmode"] = "require"
            
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args=connect_args,
            )
        return self._engine
    
    @property
    def session_factory(self):
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    @contextmanager
    def get_session(self):
        """Get a database session with context manager"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # =========================================
    # Market Data Operations
    # =========================================
    
    def get_market_data(self, limit: int = 100, orderby: str = "market_cap") -> List[Dict[str, Any]]:
        """Get market data for all coins"""
        query = text(f"""
            SELECT 
                coin_id, symbol, name, image,
                current_price as price,
                price_change_percentage_1h as change_1h,
                price_change_percentage_24h as change_24h,
                price_change_percentage_7d as change_7d,
                market_cap, market_cap_rank,
                volume_24h_usdt as volume_24h,
                high_24h, low_24h
            FROM aihub_coins
            WHERE market_cap > 0
            ORDER BY {orderby} DESC NULLS LAST
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return []
    
    def get_coin_by_id(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get single coin data"""
        query = text("""
            SELECT * FROM aihub_coins WHERE coin_id = :coin_id LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except Exception as e:
            logger.error(f"Failed to fetch coin {coin_id}: {e}")
            return None
    
    def get_ohlcv_data(self, coin_id: str, interval: str = "1h", limit: int = 200) -> List[Dict[str, Any]]:
        """Get OHLCV candlestick data"""
        symbol = self._get_symbol_for_coin(coin_id)
        
        query = text("""
            SELECT open_time as timestamp, open, high, low, close, volume
            FROM aihub_ohlcv
            WHERE symbol = :symbol
            ORDER BY open_time DESC
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol, "limit": limit})
                rows = result.fetchall()
                return [
                    {
                        "timestamp": row[0].timestamp() * 1000 if row[0] else 0,
                        "open": float(row[1]) if row[1] else 0,
                        "high": float(row[2]) if row[2] else 0,
                        "low": float(row[3]) if row[3] else 0,
                        "close": float(row[4]) if row[4] else 0,
                        "volume": float(row[5]) if row[5] else 0,
                    }
                    for row in reversed(rows)
                ]
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {coin_id}: {e}")
            return []
    
    def _get_symbol_for_coin(self, coin_id: str) -> str:
        """Get trading symbol from coin_id"""
        query = text("SELECT UPPER(symbol) FROM aihub_coins WHERE coin_id = :coin_id LIMIT 1")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                return row[0] if row else coin_id.upper()
        except Exception:
            return coin_id.upper()
    
    # =========================================
    # Sentiment Data Operations
    # =========================================
    
    def get_sentiment_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sentiment data for all coins"""
        query = text("""
            SELECT 
                s.symbol as coin_id,
                s.symbol,
                c.name,
                s.sentiment_score * 100 as asi_score,
                s.ai_signal as signal,
                s.sentiment_reason as reason,
                s.provider,
                s.analyzed_at
            FROM aihub_sentiment s
            LEFT JOIN aihub_coins c ON UPPER(c.symbol) = UPPER(s.symbol)
            ORDER BY s.analyzed_at DESC
            LIMIT :limit
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch sentiment data: {e}")
            return []
    
    def get_coin_sentiment(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get sentiment for a specific coin"""
        symbol = self._get_symbol_for_coin(coin_id)
        
        query = text("""
            SELECT 
                symbol as coin_id,
                sentiment_score * 100 as asi_score,
                ai_signal as signal,
                sentiment_reason as reason,
                provider,
                analyzed_at
            FROM aihub_sentiment
            WHERE UPPER(symbol) = :symbol
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except Exception as e:
            logger.error(f"Failed to fetch sentiment for {coin_id}: {e}")
            return None
    
    def save_sentiment(
        self,
        coin_id: str,
        asi_score: float,
        signal: str,
        reason: str,
        provider: str = "technical"
    ) -> bool:
        """Save sentiment analysis result"""
        symbol = self._get_symbol_for_coin(coin_id)
        
        query = text("""
            INSERT INTO aihub_sentiment (symbol, ai_signal, sentiment_score, sentiment_reason, provider, analyzed_at)
            VALUES (:symbol, :signal, :score, :reason, :provider, :analyzed_at)
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
                    "score": asi_score / 100.0,
                    "reason": reason,
                    "provider": provider,
                    "analyzed_at": datetime.now(),
                })
            return True
        except Exception as e:
            logger.error(f"Failed to save sentiment for {coin_id}: {e}")
            return False
    
    # =========================================
    # Portfolio Operations
    # =========================================
    
    def get_portfolio(self, user_id: str) -> List[Dict[str, Any]]:
        """Get portfolio holdings for a user"""
        query = text("""
            SELECT 
                p.coin_id, p.amount, p.buy_price, p.notes,
                p.created_at, p.updated_at,
                c.symbol, c.name, c.image, c.current_price
            FROM portfolio_holdings p
            LEFT JOIN aihub_coins c ON c.coin_id = p.coin_id
            WHERE p.user_id = :user_id
            ORDER BY p.created_at DESC
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                holdings = []
                for row in result.fetchall():
                    data = dict(row._mapping)
                    # Calculate value and PnL
                    current_price = float(data.get("current_price") or 0)
                    amount = float(data.get("amount") or 0)
                    buy_price = float(data.get("buy_price") or 0)
                    
                    data["value"] = current_price * amount
                    data["pnl"] = (current_price - buy_price) * amount
                    data["pnl_percent"] = ((current_price / buy_price) - 1) * 100 if buy_price > 0 else 0
                    
                    holdings.append(data)
                return holdings
        except Exception as e:
            logger.error(f"Failed to fetch portfolio for {user_id}: {e}")
            return []
    
    def add_holding(self, user_id: str, coin_id: str, amount: float, buy_price: float) -> bool:
        """Add a new holding"""
        query = text("""
            INSERT INTO portfolio_holdings (user_id, coin_id, amount, buy_price, created_at, updated_at)
            VALUES (:user_id, :coin_id, :amount, :buy_price, :now, :now)
            ON CONFLICT (user_id, coin_id) DO UPDATE SET
                amount = EXCLUDED.amount,
                buy_price = EXCLUDED.buy_price,
                updated_at = EXCLUDED.updated_at
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "user_id": user_id,
                    "coin_id": coin_id,
                    "amount": amount,
                    "buy_price": buy_price,
                    "now": datetime.now(),
                })
            return True
        except Exception as e:
            logger.error(f"Failed to add holding: {e}")
            return False
    
    def delete_holding(self, user_id: str, coin_id: str) -> bool:
        """Delete a holding"""
        query = text("""
            DELETE FROM portfolio_holdings
            WHERE user_id = :user_id AND coin_id = :coin_id
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {"user_id": user_id, "coin_id": coin_id})
            return True
        except Exception as e:
            logger.error(f"Failed to delete holding: {e}")
            return False
    
    # =========================================
    # On-Chain Data Operations
    # =========================================
    
    def get_onchain_signals(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get on-chain signals for a coin"""
        query = text("""
            SELECT * FROM onchain_signals WHERE coin_id = :coin_id LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"coin_id": coin_id})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except Exception as e:
            logger.error(f"Failed to fetch onchain for {coin_id}: {e}")
            return None


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get database service instance (FastAPI dependency)"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
